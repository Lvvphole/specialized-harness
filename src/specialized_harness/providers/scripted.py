"""Scripted provider - deterministic proposals for fixtures and samples (no live model)."""
from __future__ import annotations

from typing import Any

from specialized_harness.providers.base import AgentProposal, FileMutation

_FIX_ADD_APP = '''def add(a, b):
    """Return the sum of a and b."""
    return a + b
'''


def _wants_fix_add(context: dict[str, Any]) -> bool:
    task = str(context.get("task") or "")
    brief = str(context.get("task_brief") or "")
    if task == "fix_add":
        return True
    blob = f"{task} {brief}".lower()
    if "add" in blob and ("fix" in blob or "broken" in blob or "repair" in blob):
        return True
    source = str(
        context.get("fixture_source")
        or (context.get("authority") or {}).get("root")
        or ""
    )
    if "repo_add" in source.replace("\\", "/"):
        return True
    return False


class ScriptedProvider:
    """Minimum-sufficient provider: deterministic mutations for offline proofs."""

    def propose(self, node_id: str, context: dict[str, Any]) -> AgentProposal:
        task = context.get("task", "")
        run_id = context.get("run_id", "unknown")

        if node_id in ("plan",):
            return AgentProposal(plan_summary=f"scripted plan for {task}")

        if node_id in ("implement",):
            mutations: list[FileMutation] = [
                FileMutation(
                    path="harness_impl_marker.txt",
                    content=f"implemented-by:{run_id}\n",
                )
            ]
            if _wants_fix_add(context):
                inspect = context.get("repo_inspect")
                if inspect is not None:
                    try:
                        inspect.read_file("app.py")
                        inspect.search_code("def add")
                    except Exception:
                        pass
                mutations.append(FileMutation(path="app.py", content=_FIX_ADD_APP))
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
