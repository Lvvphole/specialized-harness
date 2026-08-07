"""Offline metrics over persisted run.json files (OBSERVABILITY + ECONOMICS)."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from specialized_harness.observability.persistence import load_run


@dataclass
class RunMetricsSummary:
    runs: int = 0
    accept: int = 0
    human_handoff: int = 0
    failed: int = 0
    other: int = 0
    mean_total_ms: float | None = None
    claim_pass: dict[str, int] = field(default_factory=dict)
    claim_fail: dict[str, int] = field(default_factory=dict)
    run_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        if self.runs:
            d["accept_rate"] = self.accept / self.runs
            d["handoff_rate"] = self.human_handoff / self.runs
            d["failed_rate"] = self.failed / self.runs
        else:
            d["accept_rate"] = d["handoff_rate"] = d["failed_rate"] = None
        return d


def summarize_runs_dir(runs_dir: Path | str) -> RunMetricsSummary:
    """Aggregate metrics from artifacts/runs/*/run.json (or equivalent)."""
    root = Path(runs_dir)
    summary = RunMetricsSummary()
    if not root.exists():
        return summary

    totals_ms: list[int] = []
    paths = sorted(root.glob("*/run.json"))
    for path in paths:
        data = load_run(path)
        summary.runs += 1
        rid = data.get("run_id") or path.parent.name
        summary.run_ids.append(str(rid))
        status = str(data.get("final_status", "OTHER")).upper()
        if status == "ACCEPT":
            summary.accept += 1
        elif status == "HUMAN_HANDOFF":
            summary.human_handoff += 1
        elif status == "FAILED":
            summary.failed += 1
        else:
            summary.other += 1
        if "total_ms" in data and data["total_ms"] is not None:
            totals_ms.append(int(data["total_ms"]))
        for claim in data.get("claims") or []:
            cid = str(claim.get("claim_id", "unknown"))
            verdict = str(claim.get("verdict", "")).upper()
            if verdict == "PASS":
                summary.claim_pass[cid] = summary.claim_pass.get(cid, 0) + 1
            elif verdict == "FAIL":
                summary.claim_fail[cid] = summary.claim_fail.get(cid, 0) + 1

    if totals_ms:
        summary.mean_total_ms = sum(totals_ms) / len(totals_ms)
    return summary
