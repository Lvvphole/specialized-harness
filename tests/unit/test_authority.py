"""Authority resolution: fixture vs repo+brief (AGENTS.md Q1)."""
from pathlib import Path

from specialized_harness.authority import resolve_task_authority
from specialized_harness.engine.models import FinalStatus
from specialized_harness.runner import run_fixture_task

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / "blueprints" / "standard-coding.yaml"
FIX = ROOT / "fixtures"


def test_fixture_mode_when_task_dir_exists():
    r = resolve_task_authority(FIX, "fix_add")
    assert r.ok
    assert r.mode == "fixture"
    assert r.root == (FIX / "fix_add").resolve()
    assert "fixture" in r.sources


def test_unknown_fixture_task_blocks():
    r = resolve_task_authority(FIX, "does_not_exist", allow_repo_mode=False)
    assert not r.ok
    assert "Unknown fixture task" in (r.error or "")


def test_repo_mode_requires_opt_in():
    r = resolve_task_authority(ROOT, "Fix something", allow_repo_mode=False)
    assert not r.ok


def test_repo_mode_with_brief():
    r = resolve_task_authority(ROOT, "Fix flaky invoice test", allow_repo_mode=True)
    assert r.ok
    assert r.mode == "repo"
    assert r.brief == "Fix flaky invoice test"
    assert "task_brief" in r.sources
    assert "repo" in r.sources


def test_repo_mode_missing_brief_blocks(tmp_path: Path):
    r = resolve_task_authority(tmp_path, "", allow_repo_mode=True)
    assert not r.ok
    assert "task brief" in (r.error or "").lower()


def test_repo_mode_task_md(tmp_path: Path):
    (tmp_path / "TASK.md").write_text("Repair the payment webhook timeout.\n")
    r = resolve_task_authority(tmp_path, "", allow_repo_mode=True)
    assert r.ok
    assert r.mode == "repo"
    assert "webhook" in (r.brief or "")


def test_fixture_accept_still_works():
    result = run_fixture_task(BP, FIX, "fix_add", persist=False)
    assert result.final_status == FinalStatus.ACCEPT


def test_unknown_fixture_run_fails_authority():
    result = run_fixture_task(BP, FIX, "no_such_task", persist=False)
    assert result.final_status != FinalStatus.ACCEPT
    assert result.trajectory
    assert result.trajectory[0].node_id == "resolve_authority"
