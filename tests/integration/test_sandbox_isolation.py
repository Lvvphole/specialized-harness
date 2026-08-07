"""Integration: runs must not mutate source fixtures (AGENTS.md isolation)."""
from pathlib import Path

from specialized_harness.engine.models import FinalStatus
from specialized_harness.runner import run_fixture_task
from specialized_harness.sandboxes.workspace import fingerprint_tree

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / "blueprints" / "standard-coding.yaml"
FIX = ROOT / "fixtures"


def test_accept_does_not_mutate_fixture_source():
    src = FIX / "fix_add"
    before = fingerprint_tree(src)
    result = run_fixture_task(BP, FIX, "fix_add", run_id="iso-accept-1")
    assert result.final_status == FinalStatus.ACCEPT
    assert fingerprint_tree(src) == before
    assert result.error is None or "isolation violation" not in (result.error or "")


def test_handoff_does_not_mutate_fixture_source():
    src = FIX / "always_fail_ci"
    before = fingerprint_tree(src)
    result = run_fixture_task(BP, FIX, "always_fail_ci", run_id="iso-handoff-1")
    assert result.final_status == FinalStatus.HUMAN_HANDOFF
    assert fingerprint_tree(src) == before


def test_implement_writes_only_inside_workspace_marker_in_trajectory():
    result = run_fixture_task(BP, FIX, "fix_add", run_id="iso-marker-1")
    assert result.final_status == FinalStatus.ACCEPT
    impl = next(e for e in result.trajectory if e.node_id == "implement")
    assert "harness_impl_marker.txt" in impl.metadata.get("files_changed", [])
    assert not (FIX / "fix_add" / "harness_impl_marker.txt").exists()
