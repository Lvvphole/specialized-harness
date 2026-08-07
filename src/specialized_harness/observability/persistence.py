"""Persist trajectory + ledger for offline observability (OBSERVABILITY.md)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from specialized_harness.engine.models import RunResult
from specialized_harness.observability.ledger import EvidenceLedger


def default_runs_dir() -> Path:
    return Path("artifacts") / "runs"


def serialize_run(
    result: RunResult,
    ledger: EvidenceLedger | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "run_id": result.run_id,
        "final_status": result.final_status.value
        if hasattr(result.final_status, "value")
        else str(result.final_status),
        "error": result.error,
        "total_ms": result.total_ms,
        "trajectory": [
            {
                "run_id": e.run_id,
                "node_id": e.node_id,
                "node_type": e.node_type.value
                if hasattr(e.node_type, "value")
                else str(e.node_type),
                "sequence": e.sequence,
                "started_at": e.started_at,
                "finished_at": e.finished_at,
                "exit_status": e.exit_status.value
                if hasattr(e.exit_status, "value")
                else str(e.exit_status),
                "ci_round": e.ci_round,
                "recovery_attempt": e.recovery_attempt,
                "token_usage": e.token_usage,
                "tools_called": e.tools_called,
                "artifacts": e.artifacts,
                "error": e.error,
                "metadata": e.metadata,
                "duration_ms": e.duration_ms,
            }
            for e in result.trajectory
        ],
        "claims": ledger.to_list() if ledger is not None else [],
    }
    if extra:
        payload["extra"] = extra
    return payload


def persist_run(
    result: RunResult,
    ledger: EvidenceLedger | None = None,
    *,
    runs_dir: Path | str | None = None,
    extra: dict[str, Any] | None = None,
) -> Path:
    """Write artifacts/runs/{run_id}/run.json; returns path to the file."""
    base = Path(runs_dir) if runs_dir is not None else default_runs_dir()
    out_dir = base / result.run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "run.json"
    payload = serialize_run(result, ledger, extra=extra)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def load_run(path: Path | str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
