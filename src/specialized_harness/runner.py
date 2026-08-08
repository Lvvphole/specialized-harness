"""Orchestrate a single harness run."""
from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from specialized_harness.agent_standard.inject import attach_standard_to_context
from specialized_harness.authority import resolve_task_authority
from specialized_harness.engine.blueprint_engine import BlueprintEngine
from specialized_harness.engine.loader import load_blueprint
from specialized_harness.engine.models import RunResult
from specialized_harness.nodes.registry import make_fixture_handlers, make_handlers
from specialized_harness.observability.ledger import EvidenceLedger
from specialized_harness.observability.persistence import persist_run
from specialized_harness.providers.http import resolve_provider
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
    provider: Any = None,
    provider_name: str | None = None,
    provider_url: str | None = None,
    allow_repo_mode: bool = False,
    task_brief: str | None = None,
    profile: str | None = None,
    language: str | None = None,
) -> RunResult:
    """Run a blueprint against a fixture task or a repo+brief authority root."""
    bp = load_blueprint(blueprint_path)
    root = Path(fixture_root)
    rid = run_id or str(uuid4())

    if allow_repo_mode:
        handlers, source, mode = make_handlers(root, task, allow_repo_mode=True)
        resolved = resolve_task_authority(
            root, task, task_brief=task_brief, allow_repo_mode=True
        )
        brief = resolved.brief if resolved.ok else (task_brief or task)
    else:
        source = root / task
        handlers = make_fixture_handlers(root, task)
        mode = "fixture"
        brief = None

    sandbox = WorkspaceSandbox(source if source.exists() else root / task, rid)
    selected = provider if provider is not None else resolve_provider(
        provider=provider_name, provider_url=provider_url
    )
    context: dict[str, Any] = {
        "task": task,
        "sandbox": sandbox,
        "fixture_source": (source if source.exists() else root / task).resolve(),
        "authority_root": str(root.resolve()),
        "allow_repo_mode": allow_repo_mode,
        "authority_mode": mode,
        "evidence": {},
        "ledger": EvidenceLedger(),
        "provider": selected,
        "provider_name": provider_name or type(selected).__name__,
    }
    if brief:
        context["task_brief"] = brief
    attach_standard_to_context(
        context,
        profile=profile,
        language=language,
        authority_root=root,
        required=False,
    )
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
                extra={
                    "task": task,
                    "provider": context.get("provider_name"),
                    "authority_mode": context.get("authority", {}).get("mode")
                    or mode,
                },
            )
        return result
    finally:
        if teardown:
            sandbox.teardown()
