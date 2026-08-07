"""Human-readable run summary (default CLI output)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from specialized_harness.engine.models import RunResult


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
    if result.error:
        lines.append(f"error {result.error}")
    return "\n".join(lines)
