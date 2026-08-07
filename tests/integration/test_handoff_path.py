"""Integration: HUMAN_HANDOFF path against always_fail_ci fixture."""
from pathlib import Path

from specialized_harness.engine.models import ExitStatus, FinalStatus
from specialized_harness.runner import run_fixture_task

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / "blueprints" / "standard-coding.yaml"
FIX = ROOT / "fixtures"


def test_handoff_after_two_ci_failures():
    result = run_fixture_task(BP, FIX, "always_fail_ci", run_id="test-handoff-1")
    assert result.final_status == FinalStatus.HUMAN_HANDOFF
    ids = [e.node_id for e in result.trajectory]
    assert ids.count("ci_round") == 2
    assert "fix_ci" in ids
    assert ids[-1] == "decide"
    decide = result.trajectory[-1]
    assert decide.metadata.get("final_status") == "HUMAN_HANDOFF"
    ci_events = [e for e in result.trajectory if e.node_id == "ci_round"]
    assert all(e.exit_status == ExitStatus.FAILURE for e in ci_events)
    assert ci_events[-1].ci_round == 2
    assert result.trajectory[-1].ci_round == 2
