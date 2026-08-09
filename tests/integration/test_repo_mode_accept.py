"""Repo-mode end-to-end ACCEPT (real-use proof, offline ScriptedProvider)."""
from pathlib import Path

from specialized_harness.engine.models import FinalStatus
from specialized_harness.runner import run_fixture_task

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / "blueprints" / "standard-coding.yaml"
SAMPLE = ROOT / "samples" / "repo_add"


def test_repo_mode_accept_fix_add_sample():
    assert SAMPLE.is_dir()
    assert (SAMPLE / "app.py").read_text().count("a - b") == 1

    result = run_fixture_task(
        BP,
        SAMPLE,
        "Fix the broken add function",
        allow_repo_mode=True,
        persist=False,
    )
    assert result.final_status == FinalStatus.ACCEPT
    assert any(e.node_id == "resolve_authority" for e in result.trajectory)
    assert any(e.node_id == "decide" for e in result.trajectory)
    # Sample source must remain broken (isolation)
    assert (SAMPLE / "app.py").read_text().count("a - b") == 1


SAMPLE_MUL = ROOT / "samples" / "repo_mul"


def test_repo_mode_accept_fix_mul_sample():
    assert SAMPLE_MUL.is_dir()
    assert (SAMPLE_MUL / "app.py").read_text().count("a / b") == 1

    result = run_fixture_task(
        BP,
        SAMPLE_MUL,
        "Fix the broken multiply function",
        allow_repo_mode=True,
        persist=False,
    )
    assert result.final_status == FinalStatus.ACCEPT
    assert any(e.node_id == "decide" for e in result.trajectory)
    # Sample source must remain broken (isolation)
    assert (SAMPLE_MUL / "app.py").read_text().count("a / b") == 1
