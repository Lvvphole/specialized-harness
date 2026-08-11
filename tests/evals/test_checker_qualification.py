"""Offline checker qualification — Eval harness, not ACCEPT path.

Labeled valid/invalid workspaces prove deterministic checkers discriminate.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from specialized_harness.evals.checker_qualification import (
    qualify_syntax_checker,
    qualify_tests_pass_checker,
)


@pytest.fixture
def syntax_pair(tmp_path: Path) -> tuple[Path, Path]:
    valid = tmp_path / "syntax_ok"
    invalid = tmp_path / "syntax_bad"
    valid.mkdir()
    invalid.mkdir()
    (valid / "ok.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    (invalid / "bad.py").write_text("def add(a, b)\n    return a + b\n", encoding="utf-8")
    return valid, invalid


@pytest.fixture
def tests_pair(tmp_path: Path) -> tuple[Path, Path]:
    green = tmp_path / "tests_green"
    red = tmp_path / "tests_red"
    green.mkdir()
    red.mkdir()
    (green / "test_ok.py").write_text("def test_ok():\n    assert 1 + 1 == 2\n", encoding="utf-8")
    (red / "test_bad.py").write_text("def test_bad():\n    assert 1 + 1 == 3\n", encoding="utf-8")
    return green, red


@pytest.mark.eval
def test_syntax_checker_discriminates(syntax_pair: tuple[Path, Path]) -> None:
    valid, invalid = syntax_pair
    report = qualify_syntax_checker(valid, invalid)
    assert report.discriminates(), report.to_dict()
    assert report.tp == 1 and report.tn == 1 and report.fp == 0 and report.fn == 0


@pytest.mark.eval
def test_tests_pass_checker_discriminates(tests_pair: tuple[Path, Path]) -> None:
    green, red = tests_pair
    report = qualify_tests_pass_checker(green, red)
    assert report.discriminates(), report.to_dict()
    assert report.tp == 1 and report.tn == 1 and report.fp == 0 and report.fn == 0


@pytest.mark.eval
def test_qualification_report_is_serializable(syntax_pair: tuple[Path, Path]) -> None:
    valid, invalid = syntax_pair
    d = qualify_syntax_checker(valid, invalid).to_dict()
    assert d["checker_id"] == "syntax_clean"
    assert d["discriminates"] is True
    assert len(d["cases"]) == 2
