"""Integration: max_net_loc enforced from measured workspace diffs."""
from pathlib import Path

from specialized_harness.engine.models import FinalStatus
from specialized_harness.runner import run_fixture_task

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / "blueprints" / "standard-coding.yaml"
FIX = ROOT / "fixtures"


def test_accept_path_records_measured_net_loc():
    result = run_fixture_task(BP, FIX, "fix_add", run_id="loc-accept")
    assert result.final_status == FinalStatus.ACCEPT
    impl = next(e for e in result.trajectory if e.node_id == "implement")
    assert isinstance(impl.metadata.get("net_loc"), int)
    assert impl.metadata["net_loc"] >= 1


def test_over_loc_does_not_accept():
    result = run_fixture_task(BP, FIX, "over_loc", run_id="loc-over")
    assert result.final_status != FinalStatus.ACCEPT
    statuses = {e.node_id: e for e in result.trajectory}
    if "implement" in statuses:
        net = statuses["implement"].metadata.get("net_loc")
        if net is not None:
            assert net > 1000
