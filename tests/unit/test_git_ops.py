"""Local git ops unit tests."""
from pathlib import Path
from specialized_harness.nodes.deterministic import git_ops


def test_ensure_repo_and_commit(tmp_path: Path):
    (tmp_path / "f.txt").write_text("x\n")
    r = git_ops.ensure_repo(tmp_path)
    assert r.ok
    b = git_ops.create_branch(tmp_path, "harness/test")
    assert b.ok
    c = git_ops.commit_all(tmp_path, "test commit")
    assert c.ok
    assert (tmp_path / ".git").exists()
