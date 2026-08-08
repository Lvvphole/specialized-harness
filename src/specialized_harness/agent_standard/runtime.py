from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# See full runtime in integration package — this placeholder will be replaced.
# TEMP MARKER: if you see this on main CI, the real runtime push failed.

EXECUTABLE_FAILURE_TYPES = {
    "command",
    "linter",
    "schema",
    "structural-test",
    "typecheck",
}

VALID_LEVELS = {"MUST", "CONDITIONAL", "SHOULD"}
VALID_DELIVERY = {"preload", "on_failure"}
VALID_OVERRIDE_POLICIES = {"LOCKED", "SPECIALIZABLE", "DEFAULT"}
VALID_VERIFICATION_TYPES = EXECUTABLE_FAILURE_TYPES | {"none", "semantic-review"}


class StandardError(Exception):
    pass


class StandardConfigurationError(StandardError):
    pass


class UnknownProfileError(StandardError):
    pass


class UnknownLanguageOverlayError(StandardError):
    pass


@dataclass(frozen=True)
class ContextBundle:
    text: str
    rule_ids: list[str]
    profile: str | None
    language: str | None
    governing_context_id: str


class AgentEngineeringStandard:
    def __init__(self, *args, **kwargs):
        raise StandardConfigurationError(
            "Incomplete runtime pushed; full source required"
        )

    @classmethod
    def load(cls, root: str | Path) -> "AgentEngineeringStandard":
        raise StandardConfigurationError(
            "Incomplete runtime pushed; full source required"
        )
