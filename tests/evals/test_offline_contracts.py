"""Offline eval contracts — AGENTS.md §4 outcomes (no live model).

These are the harness effectiveness floor: reproducible ACCEPT / HANDOFF / FAILED
without network. Seed eval corpus (OBSERVABILITY.md).
"""
from pathlib import Path
import subprocess
import sys

import pytest

from specialized_harness.engine.models import FinalStatus
from specialized_harness.runner import run_fixture_task

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / "blueprints" / "standard-coding.yaml"
FIX = ROOT / "fixtures"
SAMPLE = ROOT / "samples" / "repo_add"
SAMPLE_STATS = ROOT / "samples" / "repo_stats"
SAMPLE_SUB = ROOT / "samples" / "repo_sub"


@pytest.mark.eval
def test_eval_accept_fix_add():
    r = run_fixture_task(BP, FIX, "fix_add", persist=False)
    assert r.final_status == FinalStatus.ACCEPT


@pytest.mark.eval
def test_eval_handoff_always_fail_ci():
    r = run_fixture_task(BP, FIX, "always_fail_ci", persist=False)
    assert r.final_status == FinalStatus.HUMAN_HANDOFF


@pytest.mark.eval
def test_eval_failed_over_loc():
    r = run_fixture_task(BP, FIX, "over_loc", persist=False)
    assert r.final_status == FinalStatus.FAILED


@pytest.mark.eval
def test_eval_accept_repo_mode_sample():
    if not SAMPLE.is_dir():
        pytest.skip("samples/repo_add missing")
    r = run_fixture_task(
        BP,
        SAMPLE,
        "Fix the broken add function",
        allow_repo_mode=True,
        persist=False,
    )
    assert r.final_status == FinalStatus.ACCEPT


@pytest.mark.eval
def test_eval_accept_repo_mode_package_sample():
    """Corpus growth: package tree + boundary-case bug (EVAL_007)."""
    if not SAMPLE_STATS.is_dir():
        pytest.skip("samples/repo_stats missing")
    r = run_fixture_task(
        BP,
        SAMPLE_STATS,
        "Fix the broken median function",
        allow_repo_mode=True,
        persist=False,
    )
    assert r.final_status == FinalStatus.ACCEPT


@pytest.mark.eval
def test_eval_accept_repo_mode_sample_sub():
    """EVAL_009 meta-verification: unit red on source, offline ACCEPT, isolation."""
    if not SAMPLE_SUB.is_dir():
        pytest.skip("samples/repo_sub missing")
    app = SAMPLE_SUB / "app.py"
    before = app.read_text()

    # Unit contract must be red on the authoritative sample tests (not substring-only)
    red = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--tb=no", str(SAMPLE_SUB)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert red.returncode != 0, (
        "samples/repo_sub tests must fail while the tree is broken; "
        f"stdout={red.stdout!r} stderr={red.stderr!r}"
    )

    r = run_fixture_task(
        BP,
        SAMPLE_SUB,
        "Fix the broken subtract function",
        allow_repo_mode=True,
        persist=False,
    )
    assert r.final_status == FinalStatus.ACCEPT

    # Sample source must remain broken (isolation)
    assert app.read_text() == before
