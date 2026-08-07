"""Governed repo inspection tools (list_dir / read_file / search_code)."""
from pathlib import Path

import pytest

from specialized_harness.engine.models import FinalStatus
from specialized_harness.runner import run_fixture_task
from specialized_harness.sandboxes.workspace import WorkspaceError, WorkspaceSandbox
from specialized_harness.tools.repo_inspect import RepoInspect

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / "blueprints" / "standard-coding.yaml"
SAMPLE = ROOT / "samples" / "repo_add"


def test_list_read_search_and_escape(tmp_path: Path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "app.py").write_text("def add(a, b):\n    return a - b\n")
    (src / "pkg").mkdir()
    (src / "pkg" / "x.py").write_text("x = 1\n")
    sb = WorkspaceSandbox(src, "insp-1")
    sb.provision()
    try:
        ri = RepoInspect(sb)
        names = ri.list_dir(".")
        assert "app.py" in names
        body = ri.read_file("app.py")
        assert "a - b" in body
        hits = ri.search_code("def add")
        assert hits and hits[0]["path"] == "app.py"
        with pytest.raises(WorkspaceError, match="escape"):
            ri.read_file("../outside")
        with pytest.raises(WorkspaceError, match="escape"):
            ri.list_dir("../../etc")
        assert not hasattr(ri, "write_file")
        assert any(o.tool == "read_file" and o.ok for o in ri.log)
        assert ri.tools_called()
    finally:
        sb.teardown()


def test_fixture_accept_records_tools_when_scripted_reads():
    result = run_fixture_task(BP, ROOT / "fixtures", "fix_add", persist=False)
    assert result.final_status == FinalStatus.ACCEPT
    impl = next(e for e in result.trajectory if e.node_id == "implement")
    assert impl.tools_called
    assert any("read_file" in t for t in impl.tools_called)


def test_repo_mode_accept_still_with_tools():
    if not SAMPLE.is_dir():
        pytest.skip("samples/repo_add not present")
    result = run_fixture_task(
        BP,
        SAMPLE,
        "Fix the broken add function",
        allow_repo_mode=True,
        persist=False,
    )
    assert result.final_status == FinalStatus.ACCEPT
    impl = next(e for e in result.trajectory if e.node_id == "implement")
    assert impl.tools_called
