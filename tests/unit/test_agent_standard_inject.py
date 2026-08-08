"""Inject attaches candidate guidance only; ACCEPT authority unchanged."""
from __future__ import annotations

from pathlib import Path

import pytest

from specialized_harness.agent_standard.inject import (
    attach_standard_to_context,
    find_standard_root,
    load_standard,
)
from specialized_harness.agent_standard.runtime import UnknownProfileError

REPO = Path(__file__).resolve().parents[2]


def test_find_standard_root_finds_repo_agent_standard() -> None:
    root = find_standard_root(REPO)
    assert root is not None
    assert root.name == ".agent-standard"


def test_load_standard_from_repo() -> None:
    std = load_standard(REPO, required=True)
    assert std is not None
    bundle = std.compile_context(profile=None)
    assert "AD-002" in bundle.rule_ids


def test_load_standard_optional_when_missing(tmp_path: Path) -> None:
    # authority_root with no .agent-standard still falls through to CWD/packaged;
    # only assert required=False does not raise.
    result = load_standard(tmp_path, required=False)
    # May be None or packaged standard — both acceptable for optional load
    assert result is None or hasattr(result, "compile_context")


def test_attach_standard_to_context_sets_fields() -> None:
    ctx: dict = {}
    out = attach_standard_to_context(ctx, profile="general", authority_root=REPO)
    assert "agent_standard_text" in out
    assert "AD-002" in out["agent_standard_rule_ids"]
    assert out["agent_standard_profile"] == "general"
    assert out["agent_standard_governing_context_id"]


def test_attach_unknown_profile_optional_returns_unchanged() -> None:
    ctx = {"keep": True}
    out = attach_standard_to_context(
        ctx, profile="does-not-exist", authority_root=REPO, required=False
    )
    assert out == {"keep": True}


def test_attach_unknown_profile_required_raises() -> None:
    with pytest.raises(UnknownProfileError):
        attach_standard_to_context(
            {}, profile="does-not-exist", authority_root=REPO, required=True
        )


def test_packaged_standard_fallback_hook() -> None:
    from specialized_harness.agent_standard.inject import _packaged_standard_root

    # Packaged standard/ is optional in editable source trees; when present it must
    # contain config.json so installed wheels can load guidance without a checkout.
    pkg = _packaged_standard_root()
    if pkg is not None:
        assert (pkg / "config.json").is_file()
