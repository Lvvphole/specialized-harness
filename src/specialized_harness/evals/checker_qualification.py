"""Offline checker qualification — Eval harness procedure, not verification.

Runs labeled valid/invalid workspaces through deterministic checkers and
records TP/TN/FP/FN. Used to decide whether a checker is good enough to admit
into the verification harness. Never declares a coding task ACCEPT.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from specialized_harness.nodes.deterministic.checks import run_pytest, syntax_check


@dataclass
class CheckerCaseResult:
    case_id: str
    label_valid: bool
    predicted_valid: bool
    observation: str

    @property
    def classification(self) -> str:
        if self.label_valid and self.predicted_valid:
            return "TP"
        if not self.label_valid and not self.predicted_valid:
            return "TN"
        if not self.label_valid and self.predicted_valid:
            return "FP"
        return "FN"


@dataclass
class CheckerQualificationReport:
    checker_id: str
    method: str
    cases: list[CheckerCaseResult] = field(default_factory=list)

    @property
    def tp(self) -> int:
        return sum(1 for c in self.cases if c.classification == "TP")

    @property
    def tn(self) -> int:
        return sum(1 for c in self.cases if c.classification == "TN")

    @property
    def fp(self) -> int:
        return sum(1 for c in self.cases if c.classification == "FP")

    @property
    def fn(self) -> int:
        return sum(1 for c in self.cases if c.classification == "FN")

    def discriminates(self) -> bool:
        """Minimum floor: at least one TP and one TN, zero FP and zero FN."""
        return self.tp >= 1 and self.tn >= 1 and self.fp == 0 and self.fn == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "checker_id": self.checker_id,
            "method": self.method,
            "tp": self.tp,
            "tn": self.tn,
            "fp": self.fp,
            "fn": self.fn,
            "discriminates": self.discriminates(),
            "cases": [asdict(c) | {"classification": c.classification} for c in self.cases],
        }


def qualify_syntax_checker(valid_ws: Path, invalid_ws: Path) -> CheckerQualificationReport:
    """Qualify syntax_clean on one valid and one invalid workspace."""
    report = CheckerQualificationReport(checker_id="syntax_clean", method="py_compile")
    for case_id, path, label in (
        ("syntax_valid", valid_ws, True),
        ("syntax_invalid", invalid_ws, False),
    ):
        result = syntax_check(path)
        report.cases.append(
            CheckerCaseResult(
                case_id=case_id,
                label_valid=label,
                predicted_valid=result.ok,
                observation=result.stdout or result.stderr,
            )
        )
    return report


def qualify_tests_pass_checker(valid_ws: Path, invalid_ws: Path) -> CheckerQualificationReport:
    """Qualify tests_pass on one green and one red pytest workspace."""
    report = CheckerQualificationReport(checker_id="tests_pass", method="pytest")
    for case_id, path, label in (
        ("tests_green", valid_ws, True),
        ("tests_red", invalid_ws, False),
    ):
        result = run_pytest(path)
        obs = (result.stdout or "") + (result.stderr or "")
        report.cases.append(
            CheckerCaseResult(
                case_id=case_id,
                label_valid=label,
                predicted_valid=result.ok,
                observation=obs[:2000],
            )
        )
    return report
