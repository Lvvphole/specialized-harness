"""Agent Engineering Standard runtime: guidance only, no verifier authority."""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from specialized_harness.agent_standard.runtime import (
    AgentEngineeringStandard,
    StandardConfigurationError,
    UnknownProfileError,
)

REPO = Path(__file__).resolve().parents[2]
EXAMPLE = REPO / ".agent-standard"


@pytest.fixture
def standard() -> AgentEngineeringStandard:
    return AgentEngineeringStandard.load(EXAMPLE)


def test_general_is_exact_kernel(standard: AgentEngineeringStandard) -> None:
    bundle = standard.compile_context(profile=None)
    assert set(bundle.rule_ids) == {"REQ-001", "SC-001", "SC-002", "RT-006", "AD-002"}


def test_unknown_profile_does_not_silently_fallback(
    standard: AgentEngineeringStandard,
) -> None:
    with pytest.raises(UnknownProfileError):
        standard.compile_context(profile="typo-profile")


def test_typescript_overlay_is_explicit(standard: AgentEngineeringStandard) -> None:
    no_overlay = standard.compile_context(profile="bug-fix")
    ts_overlay = standard.compile_context(profile="bug-fix", language="typescript")
    assert "TS-001" not in no_overlay.rule_ids
    assert {"TS-001", "TS-002", "TS-003"} <= set(ts_overlay.rule_ids)


def test_python_overlay_is_explicit(standard: AgentEngineeringStandard) -> None:
    py_overlay = standard.compile_context(profile="code-change", language="python")
    assert {"PY-001", "PY-002"} <= set(py_overlay.rule_ids)


def test_rejected_designs_not_in_ordinary_context(
    standard: AgentEngineeringStandard,
) -> None:
    for profile in ("general", "bug-fix", "code-change", "refactor"):
        bundle = standard.compile_context(profile=profile)
        assert not any(x.startswith("RD-") for x in bundle.rule_ids)


def test_runtime_render_excludes_sources_and_paths(
    standard: AgentEngineeringStandard,
) -> None:
    bundle = standard.compile_context(profile="bug-fix", language="typescript")
    assert "sources" not in bundle.text
    assert "paths" not in bundle.text
    assert "CleanCode" not in bundle.text


def test_standard_never_returns_verifier_vocabulary_as_a_decision(
    standard: AgentEngineeringStandard,
) -> None:
    bundle = standard.compile_context(profile="general")
    assert not hasattr(bundle, "verdict")
    assert not hasattr(bundle, "status")


def test_on_failure_semantic_review_is_rejected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp) / ".agent-standard"
        shutil.copytree(EXAMPLE, tmp_root)
        bad = {
            "rules": [
                {
                    "id": "LOCAL-001",
                    "domain": "local",
                    "level": "MUST",
                    "delivery": "on_failure",
                    "instruction": "This rule is unreachable.",
                    "applies_to": {"profiles": ["bug-fix"], "languages": []},
                    "verification": {"type": "semantic-review", "ref": "review"},
                    "override_policy": "DEFAULT",
                    "sources": ["local"],
                }
            ]
        }
        (tmp_root / "local-rules").mkdir(exist_ok=True)
        (tmp_root / "local-rules" / "bad.json").write_text(
            json.dumps(bad), encoding="utf-8"
        )
        with pytest.raises(StandardConfigurationError):
            AgentEngineeringStandard.load(tmp_root)
