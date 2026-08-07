"""Integration: CI and decide use executable pytest evidence (AGENTS.md Q3-Q5)."""
from pathlib import Path

from specialized_harness.engine.models import ExitStatus, FinalStatus
from specialized_harness.runner import run_fixture_task

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / "blueprints" / "standard-coding.yaml"
FIX = ROOT / "fixtures"


def test_accept_uses_real_pytest_pass():
    result = run_fixture_task(BP, FIX, "fix_add", run_id="real-ci-accept")
    assert result.final_status == FinalStatus.ACCEPT
    ci = next(e for e in result.trajectory if e.node_id == "ci_round")
    assert ci.exit_status == ExitStatus.SUCCESS
    assert "pytest" in ci.metadata.get("command", "")
    assert ci.metadata.get("exit_code") == 0
    decide = result.trajectory[-1]
    assert decide.metadata.get("final_status") == "ACCEPT"
    assert decide.metadata.get("last_ci_ok") is True


def test_handoff_uses_real_pytest_fail_twice():
    result = run_fixture_task(BP, FIX, "always_fail_ci", run_id="real-ci-handoff")
    assert result.final_status == FinalStatus.HUMAN_HANDOFF
    ci_events = [e for e in result.trajectory if e.node_id == "ci_round"]
    assert len(ci_events) == 2
    assert all(e.exit_status == ExitStatus.FAILURE for e in ci_events)
    assert all("pytest" in e.metadata.get("command", "") for e in ci_events)
    decide = result.trajectory[-1]
    assert decide.metadata.get("final_status") == "HUMAN_HANDOFF"
    assert decide.metadata.get("last_ci_ok") is False
