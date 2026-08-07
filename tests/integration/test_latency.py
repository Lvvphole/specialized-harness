"""S4-1: per-node duration_ms and run total_ms (ECONOMICS.md scaffolding)."""
from pathlib import Path
from specialized_harness.engine.models import FinalStatus
from specialized_harness.observability.persistence import load_run
from specialized_harness.runner import run_fixture_task

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / "blueprints" / "standard-coding.yaml"
FIX = ROOT / "fixtures"


def test_accept_run_has_latency_metrics(tmp_path: Path):
    result = run_fixture_task(
        BP, FIX, "fix_add", run_id="latency-accept-1", runs_dir=tmp_path
    )
    assert result.final_status == FinalStatus.ACCEPT
    assert result.total_ms >= 0
    assert all(
        isinstance(e.duration_ms, int) and e.duration_ms >= 0 for e in result.trajectory
    )
    assert result.total_ms == sum(e.duration_ms for e in result.trajectory)
    data = load_run(tmp_path / "latency-accept-1" / "run.json")
    assert "total_ms" in data
    assert data["total_ms"] == result.total_ms
    assert all("duration_ms" in e for e in data["trajectory"])
