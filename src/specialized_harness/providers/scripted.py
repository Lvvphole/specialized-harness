"""Scripted provider - deterministic proposals for fixtures and samples (no live model)."""
from __future__ import annotations

from typing import Any

from specialized_harness.providers.base import AgentProposal, FileMutation

_FIX_ADD_APP = '''def add(a, b):
    """Return the sum of a and b."""
    return a + b
'''

_FIX_MUL_APP = '''def multiply(a, b):
    """Return the product of a and b."""
    return a * b
'''

_FIX_SUB_APP = '''def subtract(a, b):
    """Return the difference of a and b."""
    return a - b
'''

_FIX_MEDIAN_CORE = '''"""Descriptive statistics over numeric sequences."""


def mean(values):
    """Return the arithmetic mean of values."""
    if not values:
        raise ValueError("mean() requires at least one value")
    return sum(values) / len(values)


def median(values):
    """Return the median of values.

    Even-length inputs average the two middle values.
    """
    if not values:
        raise ValueError("median() requires at least one value")
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2
'''


def _wants_repair(context: dict[str, Any], subject: str, sample_dir: str) -> bool:
    """True when the brief asks to repair ``subject`` or the source is ``sample_dir``."""
    task = str(context.get("task") or "")
    brief = str(context.get("task_brief") or "")
    blob = f"{task} {brief}".lower()
    if subject in blob and ("fix" in blob or "broken" in blob or "repair" in blob):
        return True
    source = str(
        context.get("fixture_source")
        or (context.get("authority") or {}).get("root")
        or ""
    )
    return sample_dir in source.replace("\\", "/")


def _wants_fix_add(context: dict[str, Any]) -> bool:
    if str(context.get("task") or "") == "fix_add":
        return True
    return _wants_repair(context, "add", "repo_add")


def _wants_fix_mul(context: dict[str, Any]) -> bool:
    return _wants_repair(context, "multiply", "repo_mul")


def _wants_fix_median(context: dict[str, Any]) -> bool:
    return _wants_repair(context, "median", "repo_stats")


def _wants_fix_sub(context: dict[str, Any]) -> bool:
    return _wants_repair(context, "subtract", "repo_sub")


def _inspect(context: dict[str, Any], path: str, query: str) -> None:
    """Exercise the read-only inspection tools when the harness supplies them."""
    inspect = context.get("repo_inspect")
    if inspect is None:
        return
    try:
        inspect.read_file(path)
        inspect.search_code(query)
    except Exception:
        pass


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
                _inspect(context, "app.py", "def add")
                mutations.append(FileMutation(path="app.py", content=_FIX_ADD_APP))
            if _wants_fix_mul(context):
                _inspect(context, "app.py", "def multiply")
                mutations.append(FileMutation(path="app.py", content=_FIX_MUL_APP))
            if _wants_fix_sub(context):
                _inspect(context, "app.py", "def subtract")
                mutations.append(FileMutation(path="app.py", content=_FIX_SUB_APP))
            if _wants_fix_median(context):
                _inspect(context, "statskit/core.py", "def median")
                mutations.append(
                    FileMutation(path="statskit/core.py", content=_FIX_MEDIAN_CORE)
                )
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
