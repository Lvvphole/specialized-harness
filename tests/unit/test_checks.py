"""Executable check unit tests."""
from pathlib import Path
from specialized_harness.nodes.deterministic.checks import run_pytest, syntax_check


def test_syntax_check_ok(tmp_path: Path):
    (tmp_path / "ok.py").write_text("x = 1\n")
    r = syntax_check(tmp_path)
    assert r.ok


def test_syntax_check_bad(tmp_path: Path):
    (tmp_path / "bad.py").write_text("def (\n")
    r = syntax_check(tmp_path)
    assert not r.ok


def test_pytest_pass(tmp_path: Path):
    (tmp_path / "test_ok.py").write_text("def test_ok():\n    assert 1 == 1\n")
    r = run_pytest(tmp_path)
    assert r.ok
    assert r.exit_code == 0


def test_pytest_fail(tmp_path: Path):
    (tmp_path / "test_bad.py").write_text("def test_bad():\n    assert False\n")
    r = run_pytest(tmp_path)
    assert not r.ok
