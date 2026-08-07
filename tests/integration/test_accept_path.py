"""Integration: ACCEPT path against fix_add fixture."""
from pathlib import Path

from specialized_harness.engine.models import FinalStatus, NodeType
from specialized_harness.runner import run_fixture_task

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / "blueprints" / "standard-coding.yaml"
FIX = ROOT / "fixtures"


def test_accept_path_fix_add():
    result = run_fixture_task(BP, FIX, "fix_add", run_id="test-accept-1")
    assert result.final_status == FinalStatus.ACCEPT
    ids = [e.node_id for e in result.trajectory]
    assert ids[0] == "resolve_authority"
    assert "implement" in ids
    assert "ci_round" in ids
    assert ids[-1] == "decide"
    decide = result.trajectory[-1]
    assert decide.metadata.get("final_status") == "ACCEPT"
    for e in result.trajectory:
        assert e.node_id
        assert e.node_type in (NodeType.DETERMINISTIC, NodeType.AGENTIC)
        assert e.exit_status
        assert e.sequence >= 1
    assert result.trajectory[-1].ci_round == 1
