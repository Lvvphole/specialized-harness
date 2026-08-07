"""S5-1: offline run metrics over run.json."""
import json
from pathlib import Path
from specialized_harness.observability.metrics import summarize_runs_dir


def _write_run(root: Path, run_id: str, status: str, total_ms: int, claims: list):
    d = root / run_id
    d.mkdir(parents=True)
    (d / "run.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "final_status": status,
                "total_ms": total_ms,
                "trajectory": [],
                "claims": claims,
            }
        )
    )


def test_summarize_empty(tmp_path: Path):
    s = summarize_runs_dir(tmp_path)
    assert s.runs == 0
    assert s.to_dict()["accept_rate"] is None


def test_summarize_accept_and_handoff(tmp_path: Path):
    _write_run(
        tmp_path,
        "a1",
        "ACCEPT",
        100,
        [{"claim_id": "tests_pass", "verdict": "PASS"}],
    )
    _write_run(
        tmp_path,
        "h1",
        "HUMAN_HANDOFF",
        200,
        [{"claim_id": "tests_pass", "verdict": "FAIL"}],
    )
    s = summarize_runs_dir(tmp_path)
    d = s.to_dict()
    assert d["runs"] == 2
    assert d["accept"] == 1
    assert d["human_handoff"] == 1
    assert d["accept_rate"] == 0.5
    assert d["handoff_rate"] == 0.5
    assert d["mean_total_ms"] == 150.0
    assert d["claim_pass"]["tests_pass"] == 1
    assert d["claim_fail"]["tests_pass"] == 1
