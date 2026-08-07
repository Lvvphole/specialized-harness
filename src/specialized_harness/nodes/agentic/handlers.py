"""Agentic node handlers (plan / implement / fix) - propose via AgentProvider."""
from __future__ import annotations

from typing import Any, Callable

from specialized_harness.engine.models import NodeResult
from specialized_harness.nodes.agentic.apply import apply_proposal
from specialized_harness.nodes.deterministic.loc import measure_net_loc
from specialized_harness.nodes.results import fail, ok
from specialized_harness.observability.ledger import EvidenceLedger, Verdict
from specialized_harness.policy.enforcer import PolicyEnforcer, PolicyViolation
from specialized_harness.providers.base import AgentProvider
from specialized_harness.providers.scripted import ScriptedProvider
from specialized_harness.sandboxes.workspace import WorkspaceError, WorkspaceSandbox

Handler = Callable[[dict[str, Any]], NodeResult]


def build_agentic_handlers() -> dict[str, Handler]:
    def plan(ctx: dict[str, Any]) -> NodeResult:
        sandbox: WorkspaceSandbox | None = ctx.get("sandbox")
        ws = str(sandbox.root) if sandbox and sandbox.root else ""
        provider: AgentProvider = ctx.get("provider") or ScriptedProvider()
        proposal = provider.propose("plan", ctx)
        return ok(plan=proposal.plan_summary or "plan", workspace=ws)

    def implement(ctx: dict[str, Any]) -> NodeResult:
        sandbox: WorkspaceSandbox | None = ctx.get("sandbox")
        if sandbox is None or sandbox.root is None:
            return fail("Workspace not provisioned before implement")
        provider: AgentProvider = ctx.get("provider") or ScriptedProvider()
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
            return fail(str(e), **meta)
        return ok(**meta)

    def fix_ci_failures(ctx: dict[str, Any]) -> NodeResult:
        provider: AgentProvider = ctx.get("provider") or ScriptedProvider()
        proposal = provider.propose("fix_ci_failures", ctx)
        sandbox: WorkspaceSandbox | None = ctx.get("sandbox")
        files_changed: list[str] = []
        if sandbox and sandbox.root and proposal.mutations:
            try:
                files_changed = apply_proposal(sandbox, proposal)
            except WorkspaceError as e:
                return fail(str(e))
        return ok(
            attempted_fix=True,
            files_changed=files_changed,
            plan=proposal.plan_summary,
        )

    return {
        "plan": plan,
        "implement": implement,
        "fix_ci_failures": fix_ci_failures,
    }
