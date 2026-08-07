"""Node handler registry - composes deterministic + agentic handlers.

Public API unchanged: make_fixture_handlers(fixture_root, task) -> handler map.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from specialized_harness.engine.models import NodeResult
from specialized_harness.nodes.agentic.handlers import build_agentic_handlers
from specialized_harness.nodes.deterministic.handlers import build_deterministic_handlers

Handler = Callable[[dict[str, Any]], NodeResult]


def make_fixture_handlers(fixture_root: Path, task: str) -> dict[str, Handler]:
    """Handlers: mutations in sandbox; verification is executable in workspace."""
    task_dir = (fixture_root / task).resolve()
    handlers: dict[str, Handler] = {}
    handlers.update(build_deterministic_handlers(task_dir))
    handlers.update(build_agentic_handlers())
    return handlers
