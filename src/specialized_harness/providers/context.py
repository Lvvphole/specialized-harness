"""Optional proposal-request context from harness evidence (never acceptance authority)."""
from __future__ import annotations

from typing import Any


def build_propose_body(node_id: str, context: dict[str, Any]) -> dict[str, Any]:
    """Minimal required fields + optional evidence snippets when present."""
    body: dict[str, Any] = {
        "node_id": node_id,
        "task": context.get("task"),
        "run_id": context.get("run_id"),
    }
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
    return body
