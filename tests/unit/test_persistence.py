"""Trajectory + ledger persistence unit tests."""
from pathlib import Path
from specialized_harness.engine.models import (
    ExitStatus,
    FinalStatus,
    NodeType,
    RunResult,
    TrajectoryEvent,
)
from specialized_harness.observability.ledger import EvidenceLedger, Verdict
from specialized_harness.observability.persistence import load_run, persist_run, serialize_run


def _sample_result() -> RunResult:
    ev = TrajectoryEvent(
        run_id="r1",
        node_id="decide",
        node_type=NodeType.DETERMINISTIC,
        sequence=1,
        started_at="t0",
        finished_at="t1",
        exit_status=ExitStatus.SUCCESS,
        ci_round=0,
        recovery_attempt=0,
        token_usage={},
        tools_called=[],
        artifacts=[],
        error=None,
        metadata={"final_status": "ACCEPT"},
    )
    return RunResult(run_id="r1", final_status=FinalStatus.ACCEPT, trajectory=[ev])


def test_round_trip(tmp_path: Path):
    led = EvidenceLedger()
    led.append("tests_pass", "ws", "pytest", "ok", Verdict.PASS)
    path = persist_run(_sample_result(), led, runs_dir=tmp_path)
    assert path.exists()
    data = load_run(path)
    assert data["run_id"] == "r1"
    assert data["final_status"] == "ACCEPT"
    assert data["trajectory"][0]["node_id"] == "decide"
    assert data["claims"][0]["claim_id"] == "tests_pass"
    assert data["claims"][0]["verdict"] == "PASS"


def test_serialize_includes_sequence():
    data = serialize_run(_sample_result())
    assert data["trajectory"][0]["sequence"] == 1
