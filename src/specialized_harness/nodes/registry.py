"""Node handler registry - fixture-driven with disposable workspace (Sprint 2)."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from specialized_harness.engine.models import ExitStatus, FinalStatus, NodeResult
from specialized_harness.sandboxes.workspace import WorkspaceError, WorkspaceSandbox

Handler = Callable[[dict[str, Any]], NodeResult]


def _ok(artifacts: list[str] | None = None, **meta: Any) -> NodeResult:
    return NodeResult(ExitStatus.SUCCESS, artifacts=artifacts or [], metadata=meta)


def _fail(error: str, **meta: Any) -> NodeResult:
    return NodeResult(ExitStatus.FAILURE, error=error, metadata=meta)


def make_fixture_handlers(fixture_root: Path, task: str) -> dict[str, Handler]:
    """Handlers driven by fixture task; mutations target the sandbox workspace only."""
    task_dir = (fixture_root / task).resolve()
    fail_ci = task == "always_fail_ci"

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
        except WorkspaceError as e:
            return _fail(str(e))
        ctx["policy"].net_loc = len(files_changed)
        return _ok(
            files_changed=files_changed,
            net_loc=ctx["policy"].net_loc,
            workspace=str(sandbox.root),
        )

    def run_local_verification(ctx: dict[str, Any]) -> NodeResult:
        sandbox: WorkspaceSandbox | None = ctx.get("sandbox")
        ws = str(sandbox.root) if sandbox and sandbox.root else ""
        return _ok(checks=["lint", "typecheck"], workspace=ws)

    def run_local_linters(ctx: dict[str, Any]) -> NodeResult:
        return run_local_verification(ctx)

    def git_push(ctx: dict[str, Any]) -> NodeResult:
        return _ok(branch=f"harness/{ctx['run_id'][:8]}")

    def selective_ci_and_verify_outcome(ctx: dict[str, Any]) -> NodeResult:
        if fail_ci:
            return _fail("fixture CI failure", tests_failed=["test_always_fails"])
        return _ok(tests_passed=["test_add"])

    def selective_ci(ctx: dict[str, Any]) -> NodeResult:
        return selective_ci_and_verify_outcome(ctx)

    def fix_ci_failures(ctx: dict[str, Any]) -> NodeResult:
        return _ok(attempted_fix=True)

    def decide_accept_or_handoff(ctx: dict[str, Any]) -> NodeResult:
        policy = ctx["policy"]
        if fail_ci and policy.ci_rounds >= policy.max_ci_rounds:
            return _ok(final_status=FinalStatus.HUMAN_HANDOFF.value)
        if not fail_ci:
            return _ok(final_status=FinalStatus.ACCEPT.value)
        return _ok(final_status=FinalStatus.FAILED.value)

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
