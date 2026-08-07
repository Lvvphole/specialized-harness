"""S3-2: git_push never claims remote success without a remote."""
from pathlib import Path
from specialized_harness.engine.models import FinalStatus
from specialized_harness.runner import run_fixture_task

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / "blueprints" / "standard-coding.yaml"
FIX = ROOT / "fixtures"


def test_push_records_local_commit_and_skips_remote():
    result = run_fixture_task(BP, FIX, "fix_add", run_id="git-honest-1")
    assert result.final_status == FinalStatus.ACCEPT
    push = next(e for e in result.trajectory if e.node_id == "push")
    assert push.metadata.get("local_commit") is True
    assert push.metadata.get("remote_push") is False
    assert push.metadata.get("remote_push_skipped") is True
    assert push.metadata.get("skip_reason") == "no_remote_configured"
    assert push.metadata.get("branch", "").startswith("harness/")


def test_handoff_path_still_honest_on_push():
    result = run_fixture_task(BP, FIX, "always_fail_ci", run_id="git-honest-2")
    assert result.final_status == FinalStatus.HUMAN_HANDOFF
    pushes = [e for e in result.trajectory if e.node_id == "push"]
    assert len(pushes) >= 1
    for p in pushes:
        assert p.metadata.get("remote_push") is False
        assert p.metadata.get("remote_push_skipped") is True
