"""Agent provider interface - models propose; harness governs (AGENTS.md).

Providers never declare success. They only propose file mutations / plans.
Acceptance is independent (ledger + CI + policy).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass
class FileMutation:
    """Relative path under workspace + full new contents (or None to delete)."""

    path: str
    content: str | None


@dataclass
class AgentProposal:
    """What an agentic node is allowed to return to the harness."""

    mutations: list[FileMutation] = field(default_factory=list)
    plan_summary: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


@runtime_checkable
class AgentProvider(Protocol):
    """Swappable source of proposals for agentic nodes (plan/implement/fix)."""

    def propose(self, node_id: str, context: dict[str, Any]) -> AgentProposal:
        """Return a proposal; must not mutate workspace itself."""
        ...
