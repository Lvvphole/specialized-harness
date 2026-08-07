"""Node handler registry - composes deterministic + agentic handlers.

Public API: make_fixture_handlers(fixture_root, task) -> handler map.
Also: make_handlers(...) for fixture or repo authority modes.
"""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from specialized_harness.authority import resolve_task_authority
from specialized_harness.engine.models import NodeResult
from specialized_harness.nodes.agentic.handlers import build_agentic_handlers
from specialized_harness.nodes.deterministic.handlers import build_deterministic_handlers

Handler = Callable[[dict[str, Any]], NodeResult]


def make_fixture_handlers(fixture_root: Path, task: str) -> dict[str, Handler]:
    """Handlers for fixture tasks (authority = fixture directory)."""
    task_dir = (fixture_root / task).resolve()
    handlers: dict[str, Handler] = {}
    handlers.update(build_deterministic_handlers(task_dir, authority_mode="fixture"))
    handlers.update(build_agentic_handlers())
    return handlers


def make_handlers(
    root: Path,
    task: str,
    *,
    allow_repo_mode: bool = False,
) -> tuple[dict[str, Handler], Path, str]:
    """Build handlers after resolving authority.

    Returns (handlers, source_path_for_sandbox, mode).
    """
    resolved = resolve_task_authority(
        root, task, allow_repo_mode=allow_repo_mode
    )
    if not resolved.ok:
        task_dir = (
            (Path(root) / task).resolve()
            if not allow_repo_mode
            else Path(root).resolve()
        )
        handlers: dict[str, Handler] = {}
        handlers.update(
            build_deterministic_handlers(
                task_dir,
                authority_mode="repo" if allow_repo_mode else "fixture",
            )
        )
        handlers.update(build_agentic_handlers())
        return handlers, task_dir, "unknown"

    handlers = {}
    handlers.update(
        build_deterministic_handlers(
            resolved.root,
            authority_mode=resolved.mode,
        )
    )
    handlers.update(build_agentic_handlers())
    return handlers, resolved.root, resolved.mode
