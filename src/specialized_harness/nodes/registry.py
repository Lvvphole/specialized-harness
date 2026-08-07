"""Node handler registry - workspace-scoped, executable verification (Sprint 2)."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from specialized_harness.engine.models import ExitStatus, FinalStatus, NodeResult
from specialized_harness.nodes.deterministic.checks import run_pytest, syntax_check
from specialized_harness.nodes.deterministic import git_ops
from specialized_harness.nodes.deterministic.loc import measure_net_loc
from specialized_harness.nodes.agentic.apply import apply_proposal
from specialized_harness.observability.ledger import EvidenceLedger, Verdict
from specialized_harness.policy.enforcer import PolicyEnforcer, PolicyViolation
from specialized_harness.providers.base import AgentProvider
from specialized_harness.providers.scripted import ScriptedProvider
from specialized_harness.sandboxes.workspace import WorkspaceError, WorkspaceSandbox

Handler = Callable[[dict[str, Any]], NodeResult]


def _ok(artifacts: list[str] | None = None, **meta: Any) -> NodeResult:
    return NodeResult(ExitStatus.SUCCESS, artifacts=artifacts or [], metadata=meta)


def _fail(error: str, **meta: Any) -> NodeResult:
    return NodeResult(ExitStatus.FAILURE, error=error, metadata=meta)


def make_fixture_handlers(fixture_root: Path, task: str) -> dict[str, Handler]:
    """Handlers: mutations in sandbox; verification is executable in workspace."""
    task_dir = (fixture_root / task).resolve()

    def resolve_authority(ctx: dict[str, Any]) -> NodeResult:
        if not task_dir.exists():
            return _fail(f"Unknown fixture task: {task}")
        return _ok(authority_sources=["fixture", str(task_dir)])

    def constrain_scope(ctx: dict[str, Any]) -> NodeResult:
        sandbox: WorkspaceSandbox | None = ctx.get("sandbox")
        allowed = [str(sandbox.root)] if sandbox and sandbox.root else [str(task_dir)]
        return _ok(allowed_paths=allowed)

    def provision_sandbox(ctx: dict[str, Any]) -> NodeResult:
        sandbox: WorkspaceSandbox | None = ctx.get("sandbox")
        if sandbox is None:
            return _fail("No WorkspaceSandbox in context")
        try:
            root = sandbox.provision()
        except WorkspaceError as e:
            return _fail(str(e))
        return _ok(sandbox=str(root), workspace=str(root))

    def plan(ctx: dict[str, Any]) -> NodeResult:
        sandbox: WorkspaceSandbox | None = ctx.get("sandbox")
        ws = str(sandbox.root) if sandbox and sandbox.root else ""
        provider: AgentProvider = ctx.get("provider") or ScriptedProvider()
        proposal = provider.propose("plan", ctx)
        return _ok(plan=proposal.plan_summary or "plan", workspace=ws)

    def implement(ctx: dict[str, Any]) -> NodeResult:
        sandbox: WorkspaceSandbox | None = ctx.get("sandbox")
        if sandbox is None or sandbox.root is None:
            return _fail("Workspace not provisioned before implement")
        provider: AgentProvider = ctx.get("provider") or ScriptedProvider()
        proposal = provider.propose("implement", ctx)
        if proposal.error:
            return _fail(proposal.error)
        try:
            files_changed = apply_proposal(sandbox, proposal)
        except WorkspaceError as e:
            return _fail(str(e))
        net = measure_net_loc(sandbox.baseline_snapshot, sandbox.root)
        ctx["policy"].net_loc = net
        evidence = ctx.setdefault("evidence", {})
        evidence["net_loc"] = net
        meta = {
            "files_changed": files_changed,
            "net_loc": net,
            "workspace": str(sandbox.root),
            "provider": type(provider).__name__,
        }
        ledger: EvidenceLedger | None = ctx.get("ledger")
        try:
            PolicyEnforcer(ctx["policy"]).check_loc_allowed(net)
            if ledger is not None:
                ledger.append(
                    claim_id="loc_within_budget",
                    subject="workspace_diff",
                    method="measure_net_loc",
                    observation=f"net_loc={net}",
                    verdict=Verdict.PASS,
                )
        except PolicyViolation as e:
            evidence["loc_exceeded"] = True
            if ledger is not None:
                ledger.append(
                    claim_id="loc_within_budget",
                    subject="workspace_diff",
                    method="measure_net_loc",
                    observation=f"net_loc={net}",
                    verdict=Verdict.FAIL,
                )
            return _fail(str(e), **meta)
        return _ok(**meta)

    def run_local_verification(ctx: dict[str, Any]) -> NodeResult:
        sandbox: WorkspaceSandbox | None = ctx.get("sandbox")
        if sandbox is None or sandbox.root is None:
            return _fail("Workspace not provisioned before local_verify")
        result = syntax_check(sandbox.root)
        ledger: EvidenceLedger | None = ctx.get("ledger")
        if ledger is not None:
            ledger.append(
                claim_id="syntax_clean",
                subject="workspace_python",
                method="py_compile",
                observation=result.stdout[:500],
                verdict=Verdict.PASS if result.ok else Verdict.FAIL,
            )
        meta = {
            "workspace": str(sandbox.root),
            "command": result.command,
            "exit_code": result.exit_code,
            "stdout": result.stdout,
            "claims": ledger.to_list() if ledger else [],
        }
        if result.ok:
            return _ok(checks=["syntax"], **meta)
        return _fail(f"syntax check failed: {result.stdout}", **meta)

    def run_local_linters(ctx: dict[str, Any]) -> NodeResult:
        return run_local_verification(ctx)

    def git_push(ctx: dict[str, Any]) -> NodeResult:
        """Local commit + branch only. Remote push is never claimed without a remote."""
        sandbox: WorkspaceSandbox | None = ctx.get("sandbox")
        branch = f"harness/{ctx['run_id'][:8]}"
        if sandbox is None or sandbox.root is None:
            return _fail("Workspace not provisioned before git_push")
        ws = sandbox.root
        init_r = git_ops.ensure_repo(ws)
        if not init_r.ok:
            return _fail(
                f"git init failed: {init_r.stderr}",
                remote_push=False,
                remote_push_skipped=True,
                skip_reason="git_init_failed",
            )
        br = git_ops.create_branch(ws, branch)
        if not br.ok:
            return _fail(
                f"git branch failed: {br.stderr}",
                remote_push=False,
                remote_push_skipped=True,
                skip_reason="git_branch_failed",
            )
        commit_r = git_ops.commit_all(ws, f"harness run {ctx.get('run_id', '')[:8]}")
        if not commit_r.ok:
            return _fail(
                f"git commit failed: {commit_r.stderr}",
                remote_push=False,
                remote_push_skipped=True,
                skip_reason="git_commit_failed",
            )
        return _ok(
            branch=branch,
            local_commit=True,
            remote_push=False,
            remote_push_skipped=True,
            skip_reason="no_remote_configured",
            workspace=str(ws),
        )

    def selective_ci_and_verify_outcome(ctx: dict[str, Any]) -> NodeResult:
        sandbox: WorkspaceSandbox | None = ctx.get("sandbox")
        if sandbox is None or sandbox.root is None:
            return _fail("Workspace not provisioned before CI")
        result = run_pytest(sandbox.root)
        meta = {
            "workspace": str(sandbox.root),
            "command": result.command,
            "exit_code": result.exit_code,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
        evidence = ctx.setdefault("evidence", {})
        evidence["last_ci_ok"] = result.ok
        ledger: EvidenceLedger | None = ctx.get("ledger")
        if ledger is not None:
            ledger.append(
                claim_id="tests_pass",
                subject="workspace_pytest",
                method="pytest",
                observation=(result.stdout or result.stderr)[:500],
                verdict=Verdict.PASS if result.ok else Verdict.FAIL,
            )
            meta["claims"] = ledger.to_list()
        if result.ok:
            return _ok(tests_passed=True, **meta)
        return _fail("pytest failed in workspace", tests_passed=False, **meta)

    def selective_ci(ctx: dict[str, Any]) -> NodeResult:
        return selective_ci_and_verify_outcome(ctx)

    def fix_ci_failures(ctx: dict[str, Any]) -> NodeResult:
        provider: AgentProvider = ctx.get("provider") or ScriptedProvider()
        proposal = provider.propose("fix_ci_failures", ctx)
        sandbox: WorkspaceSandbox | None = ctx.get("sandbox")
        files_changed: list[str] = []
        if sandbox and sandbox.root and proposal.mutations:
            try:
                files_changed = apply_proposal(sandbox, proposal)
            except WorkspaceError as e:
                return _fail(str(e))
        return _ok(
            attempted_fix=True,
            files_changed=files_changed,
            plan=proposal.plan_summary,
        )

    def decide_accept_or_handoff(ctx: dict[str, Any]) -> NodeResult:
        """Independent declaration from ledger claims + policy counters (not the model)."""
        policy = ctx["policy"]
        evidence = ctx.get("evidence", {})
        ledger: EvidenceLedger | None = ctx.get("ledger")
        claims = ledger.to_list() if ledger else []

        if evidence.get("loc_exceeded") or (
            ledger
            and any(
                c.claim_id == "loc_within_budget" and c.verdict == Verdict.FAIL
                for c in ledger.claims
            )
        ):
            return _ok(
                final_status=FinalStatus.FAILED.value,
                reason="net_loc exceeded max_net_loc",
                net_loc=evidence.get("net_loc"),
                claims=claims,
            )

        last_ok = evidence.get("last_ci_ok")
        if ledger is not None:
            if last_ok is True and ledger.has_mandatory_pass("tests_pass"):
                return _ok(
                    final_status=FinalStatus.ACCEPT.value,
                    last_ci_ok=True,
                    net_loc=evidence.get("net_loc"),
                    claims=claims,
                )
            if last_ok is False and policy.ci_rounds >= policy.max_ci_rounds:
                return _ok(
                    final_status=FinalStatus.HUMAN_HANDOFF.value,
                    last_ci_ok=False,
                    claims=claims,
                )
            if last_ok is False:
                return _ok(
                    final_status=FinalStatus.FAILED.value,
                    last_ci_ok=False,
                    claims=claims,
                )
            return _ok(
                final_status=FinalStatus.FAILED.value,
                reason="insufficient evidence",
                claims=claims,
            )

        if last_ok is True:
            return _ok(final_status=FinalStatus.ACCEPT.value, last_ci_ok=True)
        if last_ok is False and policy.ci_rounds >= policy.max_ci_rounds:
            return _ok(final_status=FinalStatus.HUMAN_HANDOFF.value, last_ci_ok=False)
        return _ok(final_status=FinalStatus.FAILED.value, reason="no CI evidence")

    def create_pull_request(ctx: dict[str, Any]) -> NodeResult:
        """No remote PR in Minimum Sufficient path; record explicit skip then decide."""
        evidence = ctx.setdefault("evidence", {})
        evidence["pr_skipped"] = True
        evidence["pr_skip_reason"] = "no_remote_configured"
        result = decide_accept_or_handoff(ctx)
        result.metadata = {
            **result.metadata,
            "remote_pr": False,
            "remote_pr_skipped": True,
            "skip_reason": "no_remote_configured",
        }
        return result

    def hydrate_context(ctx: dict[str, Any]) -> NodeResult:
        return _ok()

    return {
        "resolve_authority": resolve_authority,
        "constrain_scope": constrain_scope,
        "provision_sandbox": provision_sandbox,
        "hydrate_context": hydrate_context,
        "plan": plan,
        "implement": implement,
        "run_local_verification": run_local_verification,
        "run_local_linters": run_local_linters,
        "git_push": git_push,
        "selective_ci_and_verify_outcome": selective_ci_and_verify_outcome,
        "selective_ci": selective_ci,
        "fix_ci_failures": fix_ci_failures,
        "decide_accept_or_handoff": decide_accept_or_handoff,
        "create_pull_request": create_pull_request,
    }
