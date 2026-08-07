"""Agentic node handlers (plan / implement / fix) - propose via AgentProvider."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from specialized_harness.engine.models import NodeResult
from specialized_harness.nodes.agentic.apply import apply_proposal
from specialized_harness.nodes.deterministic.loc import measure_net_loc
from specialized_harness.nodes.results import fail, ok
from specialized_harness.observability.ledger import EvidenceLedger, Verdict
from specialized_harness.policy.enforcer import PolicyEnforcer, PolicyViolation
from specialized_harness.providers.base import AgentProvider
from specialized_harness.providers.scripted import ScriptedProvider
from specialized_harness.providers.tokens import normalize_token_usage
from specialized_harness.sandboxes.workspace import WorkspaceError, WorkspaceSandbox
from specialized_harness.tools.repo_inspect import RepoInspect

Handler = Callable[[dict[str, Any]], NodeResult]


def ensure_repo_inspect(ctx: dict[str, Any]) -> RepoInspect | None:
    """Attach read-only RepoInspect bound to the provisioned sandbox."""
    existing = ctx.get("repo_inspect")
    if isinstance(existing, RepoInspect):
        return existing
    sandbox = ctx.get("sandbox")
    if sandbox is None or getattr(sandbox, "root", None) is None:
        return None
    inspect = RepoInspect(sandbox=sandbox)
    ctx["repo_inspect"] = inspect
    return inspect


def build_agentic_handlers() -> dict[str, Handler]:
    def plan(ctx: dict[str, Any]) -> NodeResult:
        sandbox: WorkspaceSandbox | None = ctx.get("sandbox")
        ws = str(sandbox.root) if sandbox and sandbox.root else ""
        provider: AgentProvider = ctx.get("provider") or ScriptedProvider()
        ensure_repo_inspect(ctx)
        proposal = provider.propose("plan", ctx)
        meta = {"plan": proposal.plan_summary or "plan", "workspace": ws}
        tokens = normalize_token_usage(proposal.metadata.get("token_usage"))
        if tokens:
            meta["token_usage"] = tokens
        return ok(**meta)

    def implement(ctx: dict[str, Any]) -> NodeResult:
        sandbox: WorkspaceSandbox | None = ctx.get("sandbox")
        if sandbox is None or sandbox.root is None:
            return fail("Workspace not provisioned before implement")
        provider: AgentProvider = ctx.get("provider") or ScriptedProvider()
        inspect = ensure_repo_inspect(ctx)
        proposal = provider.propose("implement", ctx)
        if proposal.error:
            return fail(proposal.error)
        try:
            files_changed = apply_proposal(sandbox, proposal)
        except WorkspaceError as e:
            return fail(str(e))
        net = measure_net_loc(sandbox.baseline_snapshot, sandbox.root)
        ctx["policy"].net_loc = net
        evidence = ctx.setdefault("evidence", {})
        evidence["net_loc"] = net
        meta: dict[str, Any] = {
            "files_changed": files_changed,
            "net_loc": net,
            "workspace": str(sandbox.root),
            "provider": type(provider).__name__,
        }
        if inspect is not None:
            meta["tools_called"] = inspect.tools_called()
            meta["tool_observations"] = inspect.observations()
        tokens = normalize_token_usage(proposal.metadata.get("token_usage"))
        if tokens:
            meta["token_usage"] = tokens
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
            return fail(str(e), **meta)
        return ok(**meta)

    def fix_ci_failures(ctx: dict[str, Any]) -> NodeResult:
        provider: AgentProvider = ctx.get("provider") or ScriptedProvider()
        ensure_repo_inspect(ctx)
        proposal = provider.propose("fix_ci_failures", ctx)
        sandbox: WorkspaceSandbox | None = ctx.get("sandbox")
        files_changed: list[str] = []
        if sandbox and sandbox.root and proposal.mutations:
            try:
                files_changed = apply_proposal(sandbox, proposal)
            except WorkspaceError as e:
                return fail(str(e))
        fix_meta: dict[str, Any] = {
            "attempted_fix": True,
            "files_changed": files_changed,
            "plan": proposal.plan_summary,
        }
        inspect = ctx.get("repo_inspect")
        if isinstance(inspect, RepoInspect):
            fix_meta["tools_called"] = inspect.tools_called()
        tokens = normalize_token_usage(proposal.metadata.get("token_usage"))
        if tokens:
            fix_meta["token_usage"] = tokens
        return ok(**fix_meta)

    return {
        "plan": plan,
        "implement": implement,
        "fix_ci_failures": fix_ci_failures,
    }
