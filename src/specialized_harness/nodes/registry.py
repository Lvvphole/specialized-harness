"""Node handler registry - workspace-scoped, executable verification (Sprint 2)."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from specialized_harness.engine.models import ExitStatus, FinalStatus, NodeResult
from specialized_harness.nodes.deterministic.checks import run_pytest, syntax_check
from specialized_harness.nodes.deterministic.loc import measure_net_loc
from specialized_harness.policy.enforcer import PolicyEnforcer, PolicyViolation
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
        return _ok(plan="fixture plan", workspace=ws)

    def implement(ctx: dict[str, Any]) -> NodeResult:
        sandbox: WorkspaceSandbox | None = ctx.get("sandbox")
        files_changed: list[str] = []
        if sandbox is None or sandbox.root is None:
            return _fail("Workspace not provisioned before implement")
        try:
            marker = sandbox.resolve("harness_impl_marker.txt")
            marker.write_text(f"implemented-by:{ctx.get('run_id', 'unknown')}\n")
            files_changed.append("harness_impl_marker.txt")
            if ctx.get("task") == "over_loc":
                bulk = sandbox.resolve("bulk_generated.py")
                bulk.write_text("\n".join(f"# line {i}" for i in range(1200)) + "\n")
                files_changed.append("bulk_generated.py")
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
        }
        try:
            PolicyEnforcer(ctx["policy"]).check_loc_allowed(net)
        except PolicyViolation as e:
            evidence["loc_exceeded"] = True
            return _fail(str(e), **meta)
        return _ok(**meta)

    def run_local_verification(ctx: dict[str, Any]) -> NodeResult:
        sandbox: WorkspaceSandbox | None = ctx.get("sandbox")
        if sandbox is None or sandbox.root is None:
            return _fail("Workspace not provisioned before local_verify")
        result = syntax_check(sandbox.root)
        meta = {
            "workspace": str(sandbox.root),
            "command": result.command,
            "exit_code": result.exit_code,
            "stdout": result.stdout,
        }
        if result.ok:
            return _ok(checks=["syntax"], **meta)
        return _fail(f"syntax check failed: {result.stdout}", **meta)

    def run_local_linters(ctx: dict[str, Any]) -> NodeResult:
        return run_local_verification(ctx)

    def git_push(ctx: dict[str, Any]) -> NodeResult:
        return _ok(branch=f"harness/{ctx['run_id'][:8]}")

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
        if result.ok:
            return _ok(tests_passed=True, **meta)
        return _fail("pytest failed in workspace", tests_passed=False, **meta)

    def selective_ci(ctx: dict[str, Any]) -> NodeResult:
        return selective_ci_and_verify_outcome(ctx)

    def fix_ci_failures(ctx: dict[str, Any]) -> NodeResult:
        return _ok(attempted_fix=True)

    def decide_accept_or_handoff(ctx: dict[str, Any]) -> NodeResult:
        """Independent declaration: CI evidence + LOC policy + counters (not the model)."""
        policy = ctx["policy"]
        evidence = ctx.get("evidence", {})
        if evidence.get("loc_exceeded"):
            return _ok(
                final_status=FinalStatus.FAILED.value,
                reason="net_loc exceeded max_net_loc",
                net_loc=evidence.get("net_loc"),
            )
        last_ok = evidence.get("last_ci_ok")
        if last_ok is True:
            return _ok(
                final_status=FinalStatus.ACCEPT.value,
                last_ci_ok=True,
                net_loc=evidence.get("net_loc"),
            )
        if last_ok is False and policy.ci_rounds >= policy.max_ci_rounds:
            return _ok(final_status=FinalStatus.HUMAN_HANDOFF.value, last_ci_ok=False)
        if last_ok is False:
            return _ok(final_status=FinalStatus.FAILED.value, last_ci_ok=False)
        return _ok(final_status=FinalStatus.FAILED.value, reason="no CI evidence")

    def create_pull_request(ctx: dict[str, Any]) -> NodeResult:
        return decide_accept_or_handoff(ctx)

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
