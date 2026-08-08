"""Inject Agent Engineering Standard into AgentProvider context only.

Never declares ACCEPT/FAIL/HANDOFF. Candidate-construction guidance only.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from specialized_harness.agent_standard.runtime import (
    AgentEngineeringStandard,
    StandardConfigurationError,
    StandardError,
    UnknownLanguageOverlayError,
    UnknownProfileError,
)


def find_standard_root(authority_root: str | Path | None = None) -> Path | None:
    """Prefer repo .agent-standard; else packaged standard next to this package tree.

    Search order:
    1. {authority_root}/.agent-standard
    2. CWD/.agent-standard
    3. repository root of this install (parents of package)
    """
    candidates: list[Path] = []
    if authority_root is not None:
        candidates.append(Path(authority_root) / ".agent-standard")
    candidates.append(Path.cwd() / ".agent-standard")
    here = Path(__file__).resolve()
    for parent in here.parents:
        cand = parent / ".agent-standard"
        if cand.is_dir() and (cand / "config.json").is_file():
            candidates.append(cand)
            break
    seen: set[Path] = set()
    for c in candidates:
        try:
            r = c.resolve()
        except OSError:
            continue
        if r in seen:
            continue
        seen.add(r)
        if r.is_dir() and (r / "config.json").is_file():
            return r
    return None


def load_standard(
    authority_root: str | Path | None = None,
    *,
    required: bool = False,
) -> AgentEngineeringStandard | None:
    root = find_standard_root(authority_root)
    if root is None:
        if required:
            raise StandardConfigurationError(
                "No .agent-standard directory with config.json found"
            )
        return None
    return AgentEngineeringStandard.load(root)


def attach_standard_to_context(
    context: dict[str, Any],
    *,
    profile: str | None = None,
    language: str | None = None,
    authority_root: str | Path | None = None,
    required: bool = False,
) -> dict[str, Any]:
    """Compile profile/language rules into context for AgentProvider.propose.

    Sets:
      agent_standard_text
      agent_standard_rule_ids
      agent_standard_governing_context_id
      agent_standard_profile
      agent_standard_language
    """
    try:
        standard = load_standard(authority_root, required=required)
    except (
        StandardError,
        StandardConfigurationError,
        UnknownProfileError,
        UnknownLanguageOverlayError,
    ):
        if required:
            raise
        return context
    if standard is None:
        return context
    bundle = standard.compile_context(profile=profile, language=language)
    context["agent_standard_text"] = bundle.text
    context["agent_standard_rule_ids"] = list(bundle.rule_ids)
    context["agent_standard_governing_context_id"] = standard.governing_context_id
    context["agent_standard_profile"] = profile or "general"
    context["agent_standard_language"] = language
    return context
