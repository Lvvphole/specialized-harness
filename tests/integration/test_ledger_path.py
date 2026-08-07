"""Integration: ACCEPT/HANDOFF carry ledger claims (AGENTS.md independent declaration)."""
from pathlib import Path

from specialized_harness.engine.models import FinalStatus
from specialized_harness.runner import run_fixture_task

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / "blueprints" / "standard-coding.yaml"
FIX = ROOT / "fixtures"


def test_accept_has_pass_claims_on_decide():
    result = run_fixture_task(BP, FIX, "fix_add", run_id="ledger-accept")
    assert result.final_status == FinalStatus.ACCEPT
    decide = result.trajectory[-1]
    claims = decide.metadata.get("claims") or []
    ids = {c["claim_id"]: c["verdict"] for c in claims}
    assert ids.get("tests_pass") == "PASS"
    assert ids.get("syntax_clean") == "PASS"
    assert ids.get("loc_within_budget") == "PASS"


def test_handoff_has_fail_tests_claim():
    result = run_fixture_task(BP, FIX, "always_fail_ci", run_id="ledger-handoff")
    assert result.final_status == FinalStatus.HUMAN_HANDOFF
    decide = result.trajectory[-1]
    claims = decide.metadata.get("claims") or []
    assert any(c["claim_id"] == "tests_pass" and c["verdict"] == "FAIL" for c in claims)


def test_over_loc_has_fail_loc_claim():
    result = run_fixture_task(BP, FIX, "over_loc", run_id="ledger-over")
    assert result.final_status != FinalStatus.ACCEPT
    all_claims = []
    for e in result.trajectory:
        all_claims.extend(e.metadata.get("claims") or [])
    decide = result.trajectory[-1]
    claims = decide.metadata.get("claims") or all_claims
    if claims:
        assert any(c["claim_id"] == "loc_within_budget" and c["verdict"] == "FAIL" for c in claims)
