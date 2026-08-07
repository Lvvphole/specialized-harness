"""Deterministic node handlers (authority, verify, git, decide)."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from specialized_harness.engine.models import FinalStatus, NodeResult
from specialized_harness.nodes.deterministic import git_ops
from specialized_harness.nodes.deterministic.checks import run_pytest, syntax_check
from specialized_harness.nodes.results import fail, ok
from specialized_harness.observability.ledger import EvidenceLedger, Verdict
from specialized_harness.sandboxes.workspace import WorkspaceError, WorkspaceSandbox

Handler = Callable[[dict[str, Any]], NodeResult]


def build_deterministic_handlers(task_dir: Path) -> dict[str, Handler]:
    def resolve_authority(ctx: dict[str, Any]) -> NodeResult:
        if not task_dir.exists():
            return fail(f"Unknown fixture task: {task_dir.name}")
        return ok(authority_sources=["fixture", str(task_dir)])

    def constrain_scope(ctx: dict[str, Any]) -> NodeResult:
        sandbox: WorkspaceSandbox | None = ctx.get("sandbox")
        allowed = [str(sandbox.root)] if sandbox and sandbox.root else [str(task_dir)]
        return ok(allowed_paths=allowed)

    def provision_sandbox(ctx: dict[str, Any]) -> NodeResult:
        sandbox: WorkspaceSandbox | None = ctx.get("sandbox")
        if sandbox is None:
            return fail("No WorkspaceSandbox in context")
        try:
            root = sandbox.provision()
        except WorkspaceError as e:
            return fail(str(e))
        return ok(sandbox=str(root), workspace=str(root))

    def run_local_verification(ctx: dict[str, Any]) -> NodeResult:
        sandbox: WorkspaceSandbox | None = ctx.get("sandbox")
        if sandbox is None or sandbox.root is None:
            return fail("Workspace not provisioned before local_verify")
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
            return ok(checks=["syntax"], **meta)
        return fail(f"syntax check failed: {result.stdout}", **meta)

    def run_local_linters(ctx: dict[str, Any]) -> NodeResult:
        return run_local_verification(ctx)

    def git_push(ctx: dict[str, Any]) -> NodeResult:
        sandbox: WorkspaceSandbox | None = ctx.get("sandbox")
        branch = f"harness/{ctx['run_id'][:8]}"
        if sandbox is None or sandbox.root is None:
            return fail("Workspace not provisioned before git_push")
        ws = sandbox.root
        init_r = git_ops.ensure_repo(ws)
        if not init_r.ok:
            return fail(
                f"git init failed: {init_r.stderr}",
                remote_push=False,
                remote_push_skipped=True,
                skip_reason="git_init_failed",
            )
        br = git_ops.create_branch(ws, branch)
        if not br.ok:
            return fail(
                f"git branch failed: {br.stderr}",
                remote_push=False,
                remote_push_skipped=True,
                skip_reason="git_branch_failed",
            )
        commit_r = git_ops.commit_all(ws, f"harness run {ctx.get('run_id', '')[:8]}")
        if not commit_r.ok:
            return fail(
                f"git commit failed: {commit_r.stderr}",
                remote_push=False,
                remote_push_skipped=True,
                skip_reason="git_commit_failed",
            )
        return ok(
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
            return fail("Workspace not provisioned before CI")
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
            return ok(tests_passed=True, **meta)
        return fail("pytest failed in workspace", tests_passed=False, **meta)

    def selective_ci(ctx: dict[str, Any]) -> NodeResult:
        return selective_ci_and_verify_outcome(ctx)

    def decide_accept_or_handoff(ctx: dict[str, Any]) -> NodeResult:
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
            return ok(
                final_status=FinalStatus.FAILED.value,
                reason="net_loc exceeded max_net_loc",
                net_loc=evidence.get("net_loc"),
                claims=claims,
            )

        last_ok = evidence.get("last_ci_ok")
        if ledger is not None:
            if last_ok is True and ledger.has_mandatory_pass("tests_pass"):
                return ok(
                    final_status=FinalStatus.ACCEPT.value,
                    last_ci_ok=True,
                    net_loc=evidence.get("net_loc"),
                    claims=claims,
                )
            if last_ok is False and policy.ci_rounds >= policy.max_ci_rounds:
                return ok(
                    final_status=FinalStatus.HUMAN_HANDOFF.value,
                    last_ci_ok=False,
                    claims=claims,
                )
            if last_ok is False:
                return ok(
                    final_status=FinalStatus.FAILED.value,
                    last_ci_ok=False,
                    claims=claims,
                )
            return ok(
                final_status=FinalStatus.FAILED.value,
                reason="insufficient evidence",
                claims=claims,
            )

        if last_ok is True:
            return ok(final_status=FinalStatus.ACCEPT.value, last_ci_ok=True)
        if last_ok is False and policy.ci_rounds >= policy.max_ci_rounds:
            return ok(final_status=FinalStatus.HUMAN_HANDOFF.value, last_ci_ok=False)
        return ok(final_status=FinalStatus.FAILED.value, reason="no CI evidence")

    def create_pull_request(ctx: dict[str, Any]) -> NodeResult:
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
        return ok()

    return {
        "resolve_authority": resolve_authority,
        "constrain_scope": constrain_scope,
        "provision_sandbox": provision_sandbox,
        "hydrate_context": hydrate_context,
        "run_local_verification": run_local_verification,
        "run_local_linters": run_local_linters,
        "git_push": git_push,
        "selective_ci_and_verify_outcome": selective_ci_and_verify_outcome,
        "selective_ci": selective_ci,
        "decide_accept_or_handoff": decide_accept_or_handoff,
        "create_pull_request": create_pull_request,
    }
