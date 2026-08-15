"""Repo-mode end-to-end ACCEPT (real-use proof, offline ScriptedProvider)."""
from pathlib import Path

from specialized_harness.engine.models import FinalStatus
from specialized_harness.nodes.deterministic.checks import run_pytest
from specialized_harness.runner import run_fixture_task
from specialized_harness.sandboxes.workspace import WorkspaceSandbox, fingerprint_tree

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / "blueprints" / "standard-coding.yaml"
SAMPLE = ROOT / "samples" / "repo_add"


def _run_unit_red_in_workspace_sandbox(sample: Path):
    """Unit-red via harness containment: WorkspaceSandbox + run_pytest."""
    sandbox = WorkspaceSandbox(sample, run_id="unit-red-meta")
    try:
        workspace = sandbox.provision()
        result = run_pytest(workspace, timeout_s=60)
        assert sandbox.source_unchanged()
        return result
    finally:
        sandbox.teardown()


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


SAMPLE_STATS = ROOT / "samples" / "repo_stats"
STATS_BUG = "return ordered[len(ordered) // 2]"


def test_repo_mode_accept_fix_median_sample():
    """Third sample: package tree (not flat) + boundary-case bug (not operator swap)."""
    core = SAMPLE_STATS / "statskit" / "core.py"
    assert core.is_file()
    assert core.read_text().count(STATS_BUG) == 1

    result = run_fixture_task(
        BP,
        SAMPLE_STATS,
        "Fix the broken median function",
        allow_repo_mode=True,
        persist=False,
    )
    assert result.final_status == FinalStatus.ACCEPT
    assert any(e.node_id == "decide" for e in result.trajectory)
    # The repair lands on a nested module, not a top-level app.py
    implement = next(e for e in result.trajectory if e.node_id == "implement")
    assert "statskit/core.py" in implement.metadata["files_changed"]
    # Sample source must remain broken (isolation)
    assert core.read_text().count(STATS_BUG) == 1


SAMPLE_SUB = ROOT / "samples" / "repo_sub"


def test_repo_mode_accept_fix_sub_sample():
    assert SAMPLE_SUB.is_dir()
    before = fingerprint_tree(SAMPLE_SUB)

    red = _run_unit_red_in_workspace_sandbox(SAMPLE_SUB)
    assert red.exit_code == 1, (
        f"expected TESTS_FAILED (1), got {red.exit_code}; "
        f"stdout={red.stdout!r} stderr={red.stderr!r}"
    )

    result = run_fixture_task(
        BP,
        SAMPLE_SUB,
        "Fix the broken subtract function",
        allow_repo_mode=True,
        persist=False,
    )
    assert result.final_status == FinalStatus.ACCEPT
    assert any(e.node_id == "decide" for e in result.trajectory)
    assert result.error is None or "isolation violation" not in (result.error or "")
    # Whole sample tree isolation (not app.py only)
    assert fingerprint_tree(SAMPLE_SUB) == before
    assert not (SAMPLE_SUB / "harness_impl_marker.txt").exists()
