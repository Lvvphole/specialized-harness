"""S3-3: full runs write artifacts/runs/{run_id}/run.json."""
from pathlib import Path
from specialized_harness.engine.models import FinalStatus
from specialized_harness.observability.persistence import load_run
from specialized_harness.runner import run_fixture_task

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / "blueprints" / "standard-coding.yaml"
FIX = ROOT / "fixtures"


def test_accept_run_persists_trajectory_and_claims(tmp_path: Path):
    result = run_fixture_task(
        BP, FIX, "fix_add", run_id="persist-accept-1", runs_dir=tmp_path
    )
    assert result.final_status == FinalStatus.ACCEPT
    path = tmp_path / "persist-accept-1" / "run.json"
    assert path.exists()
    data = load_run(path)
    assert data["final_status"] == "ACCEPT"
    assert len(data["trajectory"]) >= 5
    assert any(e["node_id"] == "decide" for e in data["trajectory"])
    claim_ids = {c["claim_id"]: c["verdict"] for c in data["claims"]}
    assert claim_ids.get("tests_pass") == "PASS"
    assert claim_ids.get("syntax_clean") == "PASS"


def test_handoff_run_persists_fail_claims(tmp_path: Path):
    result = run_fixture_task(
        BP, FIX, "always_fail_ci", run_id="persist-handoff-1", runs_dir=tmp_path
    )
    assert result.final_status == FinalStatus.HUMAN_HANDOFF
    data = load_run(tmp_path / "persist-handoff-1" / "run.json")
    assert data["final_status"] == "HUMAN_HANDOFF"
    assert any(
        c["claim_id"] == "tests_pass" and c["verdict"] == "FAIL" for c in data["claims"]
    )
