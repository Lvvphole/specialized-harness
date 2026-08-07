"""Orchestrate a single harness run."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from specialized_harness.engine.blueprint_engine import BlueprintEngine
from specialized_harness.engine.loader import load_blueprint
from specialized_harness.engine.models import RunResult
from specialized_harness.nodes.registry import make_fixture_handlers


def run_fixture_task(
    blueprint_path: str | Path,
    fixture_root: str | Path,
    task: str,
    run_id: str | None = None,
) -> RunResult:
    bp = load_blueprint(blueprint_path)
    handlers = make_fixture_handlers(Path(fixture_root), task)
    engine = BlueprintEngine(bp, handlers, run_id=run_id, context={"task": task})
    return engine.run()


def run_with_handlers(
    blueprint: dict[str, Any],
    handlers: dict,
    context: dict[str, Any] | None = None,
    run_id: str | None = None,
) -> RunResult:
    engine = BlueprintEngine(blueprint, handlers, run_id=run_id, context=context or {})
    return engine.run()
