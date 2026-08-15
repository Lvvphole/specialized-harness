"""Offline eval contracts — AGENTS.md §4 outcomes (no live model).

These are the harness effectiveness floor: reproducible ACCEPT / HANDOFF / FAILED
without network. Seed eval corpus (OBSERVABILITY.md).
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from specialized_harness.engine.models import FinalStatus
from specialized_harness.runner import run_fixture_task
from specialized_harness.sandboxes.workspace import fingerprint_tree

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / "blueprints" / "standard-coding.yaml"
FIX = ROOT / "fixtures"
SAMPLE = ROOT / "samples" / "repo_add"
SAMPLE_STATS = ROOT / "samples" / "repo_stats"
SAMPLE_SUB = ROOT / "samples" / "repo_sub"


def _run_unit_red_in_disposable_copy(sample: Path) -> subprocess.CompletedProcess[str]:
    """Execute sample tests against a disposable copy (not the source tree)."""
    with tempfile.TemporaryDirectory(prefix="harness-unit-red-") as td:
        copy = Path(td) / sample.name
        shutil.copytree(sample, copy)
        return subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "--tb=no", str(copy)],
            capture_output=True,
            text=True,
            cwd=str(copy),
        )


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

    before = fingerprint_tree(SAMPLE_SUB)

    # Unit contract red against a disposable copy (never the checked-out source)
    red = _run_unit_red_in_disposable_copy(SAMPLE_SUB)
    assert red.returncode == 1, (
        "samples/repo_sub must fail with TESTS_FAILED (exit 1) while broken; "
        f"got {red.returncode}; stdout={red.stdout!r} stderr={red.stderr!r}"
    )
    assert "test_subtract" in red.stdout or "FAILED" in red.stdout

    r = run_fixture_task(
        BP,
        SAMPLE_SUB,
        "Fix the broken subtract function",
        allow_repo_mode=True,
        persist=False,
    )
    assert r.final_status == FinalStatus.ACCEPT
    assert r.error is None or "isolation violation" not in (r.error or "")

    # Whole sample tree isolation (app.py, test_app.py, README, no leaked marker)
    assert fingerprint_tree(SAMPLE_SUB) == before
    assert not (SAMPLE_SUB / "harness_impl_marker.txt").exists()
