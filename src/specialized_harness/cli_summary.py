"""Human-readable run summary (default CLI output)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from specialized_harness.engine.models import RunResult


def _last_node_diagnostic(result: RunResult) -> str | None:
    """Concrete failure text from the trajectory, quoted as WRITING_STYLE requires.

    RunResult.error only carries run-level failures. A node that fails (unknown
    task, unprovisioned workspace, LOC violation) records its diagnostic on its
    trajectory event, which the summary would otherwise never show.
    """
    for event in reversed(result.trajectory):
        if event.error:
            return f"{event.node_id}: {event.error}"
    return None


def format_run_summary(
    result: RunResult,
    *,
    task: str | None = None,
    provider: str | None = None,
    claims: list[dict[str, Any]] | None = None,
    runs_dir: str | Path | None = None,
) -> str:
    status = result.final_status.value
    parts = [
        f"{status}",
        f"task={task or '-'}",
        f"provider={provider or '-'}",
        f"{len(result.trajectory)} nodes",
        f"{result.total_ms}ms",
    ]
    lines = ["  ".join(parts)]

    if claims:
        passed = [
            c["claim_id"]
            for c in claims
            if str(c.get("verdict", "")).upper() == "PASS"
        ]
        failed = [
            c["claim_id"]
            for c in claims
            if str(c.get("verdict", "")).upper() == "FAIL"
        ]
        if passed:
            lines.append("PASS  " + " · ".join(passed))
        if failed:
            lines.append("FAIL  " + " · ".join(failed))

    run_path = Path(runs_dir or "artifacts/runs") / result.run_id / "run.json"
    lines.append(f"run   {run_path.as_posix()}")
    diagnostic = result.error or _last_node_diagnostic(result)
    if diagnostic:
        lines.append(f"error {diagnostic}")
    return "\n".join(lines)
