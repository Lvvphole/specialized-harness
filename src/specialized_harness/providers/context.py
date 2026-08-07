"""Optional proposal-request context from harness evidence (never acceptance authority)."""
from __future__ import annotations

from typing import Any

ALLOWED_TOOLS = ("list_dir", "read_file", "search_code")


def build_propose_body(
    node_id: str,
    context: dict[str, Any],
    *,
    round: int = 0,
    observations: list[dict[str, Any]] | None = None,
    max_tool_rounds: int | None = None,
) -> dict[str, Any]:
    """Minimal required fields + optional evidence + multi-round tool protocol."""
    body: dict[str, Any] = {
        "node_id": node_id,
        "task": context.get("task"),
        "run_id": context.get("run_id"),
        "round": int(round),
        "allowed_tools": list(ALLOWED_TOOLS),
    }
    if max_tool_rounds is not None:
        body["max_tool_rounds"] = int(max_tool_rounds)
    brief = context.get("task_brief")
    if brief:
        body["task_brief"] = brief
    evidence = context.get("evidence") or {}
    if "net_loc" in evidence:
        body["net_loc"] = evidence["net_loc"]
    if "loc_exceeded" in evidence:
        body["loc_exceeded"] = bool(evidence["loc_exceeded"])
    if "last_ci_ok" in evidence:
        body["last_ci_ok"] = evidence["last_ci_ok"]
    stdout = evidence.get("last_ci_stdout")
    if stdout:
        body["last_ci_stdout"] = str(stdout)[:2000]
    if observations is not None:
        body["observations"] = observations
    return body
