"""Scripted provider - deterministic proposals for fixtures (no live model)."""
from __future__ import annotations

from typing import Any

from specialized_harness.providers.base import AgentProposal, FileMutation


class ScriptedProvider:
    """Minimum-sufficient provider: task-keyed file mutations for proofs."""

    def propose(self, node_id: str, context: dict[str, Any]) -> AgentProposal:
        task = context.get("task", "")
        run_id = context.get("run_id", "unknown")

        if node_id in ("plan",):
            return AgentProposal(plan_summary=f"scripted plan for {task}")

        if node_id in ("implement",):
            mutations = [
                FileMutation(
                    path="harness_impl_marker.txt",
                    content=f"implemented-by:{run_id}\n",
                )
            ]
            if task == "over_loc":
                mutations.append(
                    FileMutation(
                        path="bulk_generated.py",
                        content="\n".join(f"# line {i}" for i in range(1200)) + "\n",
                    )
                )
            return AgentProposal(mutations=mutations, plan_summary="scripted implement")

        if node_id in ("fix_ci_failures", "fix_ci"):
            return AgentProposal(
                plan_summary="scripted fix attempt", metadata={"attempted_fix": True}
            )

        return AgentProposal(plan_summary=f"no-op for {node_id}")
