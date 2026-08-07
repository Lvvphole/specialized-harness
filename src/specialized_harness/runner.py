"""Orchestrate a single harness run."""
from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from specialized_harness.engine.blueprint_engine import BlueprintEngine
from specialized_harness.engine.loader import load_blueprint
from specialized_harness.engine.models import RunResult
from specialized_harness.nodes.registry import make_fixture_handlers
from specialized_harness.observability.ledger import EvidenceLedger
from specialized_harness.observability.persistence import persist_run
from specialized_harness.providers.http import provider_from_env
from specialized_harness.sandboxes.workspace import WorkspaceSandbox


def run_fixture_task(
    blueprint_path: str | Path,
    fixture_root: str | Path,
    task: str,
    run_id: str | None = None,
    *,
    teardown: bool = True,
    persist: bool = True,
    runs_dir: str | Path | None = None,
) -> RunResult:
    """Run a blueprint against a fixture task inside a disposable workspace."""
    bp = load_blueprint(blueprint_path)
    source = Path(fixture_root) / task
    rid = run_id or str(uuid4())
    sandbox = WorkspaceSandbox(source, rid)
    handlers = make_fixture_handlers(Path(fixture_root), task)
    context: dict[str, Any] = {
        "task": task,
        "sandbox": sandbox,
        "fixture_source": source.resolve(),
        "evidence": {},  # mutable bag shared across nodes (CI outcomes, etc.)
        "ledger": EvidenceLedger(),
        "provider": provider_from_env(),
    }
    try:
        engine = BlueprintEngine(bp, handlers, run_id=rid, context=context)
        result = engine.run()
        if sandbox._source_fingerprint and not sandbox.source_unchanged():
            result.error = (
                (result.error or "")
                + " | isolation violation: fixture source mutated"
            ).strip(" |")
        if persist:
            ledger = context.get("ledger")
            persist_run(
                result,
                ledger if isinstance(ledger, EvidenceLedger) else None,
                runs_dir=runs_dir,
                extra={"task": task},
            )
        return result
    finally:
        if teardown:
            sandbox.teardown()


def run_with_handlers(
    blueprint: dict[str, Any],
    handlers: dict,
    context: dict[str, Any] | None = None,
    run_id: str | None = None,
) -> RunResult:
    engine = BlueprintEngine(blueprint, handlers, run_id=run_id, context=context or {})
    return engine.run()
