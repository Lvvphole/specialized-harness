"""Shared NodeResult helpers for handlers."""
from __future__ import annotations

from typing import Any

from specialized_harness.engine.models import ExitStatus, NodeResult


def ok(artifacts: list[str] | None = None, **meta: Any) -> NodeResult:
    return NodeResult(ExitStatus.SUCCESS, artifacts=artifacts or [], metadata=meta)


def fail(error: str, **meta: Any) -> NodeResult:
    return NodeResult(ExitStatus.FAILURE, error=error, metadata=meta)
