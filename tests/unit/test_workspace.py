"""Workspace sandbox isolation tests (Sprint 2 / S2-1)."""
from pathlib import Path
import pytest
from specialized_harness.sandboxes.workspace import WorkspaceError, WorkspaceSandbox, fingerprint_tree


def test_provision_copies_not_links(tmp_path: Path):
    src = tmp_path / "fixture"
    src.mkdir()
    (src / "app.py").write_text("x = 1\n")
    sb = WorkspaceSandbox(src, "run-a")
    root = sb.provision()
    assert root.is_dir()
    assert (root / "app.py").read_text() == "x = 1\n"
    (root / "app.py").write_text("x = 2\n")
    assert (src / "app.py").read_text() == "x = 1\n"
    assert sb.source_unchanged()
    sb.teardown()
    assert not root.exists()


def test_distinct_workspaces_for_distinct_runs(tmp_path: Path):
    src = tmp_path / "fixture"
    src.mkdir()
    (src / "f.txt").write_text("ok")
    a = WorkspaceSandbox(src, "run-1")
    b = WorkspaceSandbox(src, "run-2")
    ra, rb = a.provision(), b.provision()
    assert ra != rb
    a.teardown()
    b.teardown()


def test_path_escape_rejected(tmp_path: Path):
    src = tmp_path / "fixture"
    src.mkdir()
    (src / "a.txt").write_text("a")
    sb = WorkspaceSandbox(src, "run-esc")
    sb.provision()
    with pytest.raises(WorkspaceError, match="escapes"):
        sb.resolve("../outside.txt")
    sb.teardown()


def test_fingerprint_stable(tmp_path: Path):
    src = tmp_path / "fixture"
    src.mkdir()
    (src / "a.txt").write_text("hello")
    fp1 = fingerprint_tree(src)
    fp2 = fingerprint_tree(src)
    assert fp1 == fp2
    (src / "a.txt").write_text("changed")
    assert fingerprint_tree(src) != fp1
