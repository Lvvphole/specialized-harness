"""Node handler registry - fixture-driven for Sprint 1."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from specialized_harness.engine.models import ExitStatus, FinalStatus, NodeResult

Handler = Callable[[dict[str, Any]], NodeResult]


def _ok(artifacts: list[str] | None = None, **meta: Any) -> NodeResult:
    return NodeResult(ExitStatus.SUCCESS, artifacts=artifacts or [], metadata=meta)


def _fail(error: str, **meta: Any) -> NodeResult:
    return NodeResult(ExitStatus.FAILURE, error=error, metadata=meta)


def make_fixture_handlers(fixture_root: Path, task: str) -> dict[str, Handler]:
    """Handlers driven by fixture task name for accept / handoff proofs."""
    task_dir = fixture_root / task
    fail_ci = task == "always_fail_ci"

    def resolve_authority(ctx: dict[str, Any]) -> NodeResult:
        if not task_dir.exists():
            return _fail(f"Unknown fixture task: {task}")
        return _ok(authority_sources=["fixture", str(task_dir)])

    def constrain_scope(ctx: dict[str, Any]) -> NodeResult:
        return _ok(allowed_paths=[str(task_dir)])

    def provision_sandbox(ctx: dict[str, Any]) -> NodeResult:
        return _ok(sandbox=str(task_dir))

    def plan(ctx: dict[str, Any]) -> NodeResult:
        return _ok(plan="fixture plan")

    def implement(ctx: dict[str, Any]) -> NodeResult:
        ctx["policy"].net_loc = 12
        return _ok(files_changed=["src/app.py"], net_loc=12)

    def run_local_verification(ctx: dict[str, Any]) -> NodeResult:
        return _ok(checks=["lint", "typecheck"])

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
