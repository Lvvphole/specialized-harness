"""
Blueprint Engine — the state machine that owns phase transitions.

This module is the runtime embodiment of the invariants in AGENTS.md
and CONSTRAINTS.md. It refuses illegal transitions (especially any
attempt to exceed max_ci_rounds).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import hashlib
import json


class NodeType(str, Enum):
    DETERMINISTIC = "deterministic"
    AGENTIC = "agentic"


class ExitStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class NodeResult:
    status: ExitStatus
    artifacts: List[str] = field(default_factory=list)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyState:
    ci_rounds: int = 0
    recovery_attempts: int = 0
    max_ci_rounds: int = 2
    max_agentic_recovery_attempts: int = 1

    def can_start_ci_round(self) -> bool:
        return self.ci_rounds < self.max_ci_rounds

    def record_ci_round(self) -> None:
        if not self.can_start_ci_round():
            raise RuntimeError(
                "Policy violation: attempt to start CI round beyond max_ci_rounds=2"
            )
        self.ci_rounds += 1

    def can_recover(self) -> bool:
        return self.recovery_attempts < self.max_agentic_recovery_attempts

    def record_recovery(self) -> None:
        if not self.can_recover():
            raise RuntimeError(
                "Policy violation: recovery attempts exhausted"
            )
        self.recovery_attempts += 1


@dataclass
class TrajectoryEvent:
    run_id: str
    node_id: str
    node_type: NodeType
    sequence: int
    started_at: str
    finished_at: str
    exit_status: ExitStatus
    ci_round: int
    recovery_attempt: int
    token_usage: Dict[str, int]
    tools_called: List[str]
    artifacts: List[str]
    error: Optional[str]
    metadata: Dict[str, Any]

    def canonical_hash(self) -> str:
        payload = json.dumps(self.__dict__, sort_keys=True, default=str)
        return hashlib.sha256(payload.encode()).hexdigest()


class BlueprintEngine:
    """
    Minimal skeleton of the state machine.

    Production implementations must:
    - Load and validate the blueprint against the schema in BLUEPRINTS.md
    - Enforce every edge condition and policy counter
    - Emit a complete trajectory
    - Refuse any transition that would violate CONSTRAINTS.md
    """

    def __init__(self, blueprint: Dict[str, Any], run_id: str):
        self.blueprint = blueprint
        self.run_id = run_id
        self.policy = PolicyState(
            max_ci_rounds=blueprint.get("spec", {}).get("policy", {}).get("max_ci_rounds", 2),
            max_agentic_recovery_attempts=blueprint.get("spec", {})
            .get("policy", {})
            .get("max_agentic_recovery_attempts", 1),
        )
        self.trajectory: List[TrajectoryEvent] = []
        self.current_node_id: Optional[str] = None
        self.sequence = 0

        # Static safety check
        if self.policy.max_ci_rounds > 2:
            raise ValueError(
                "Hard constraint violation: max_ci_rounds cannot exceed 2 "
                "(see CONSTRAINTS.md and AGENTS.md)"
            )

    def start(self) -> None:
        """Begin execution at the first node."""
        nodes = self.blueprint.get("spec", {}).get("nodes", [])
        if not nodes:
            raise ValueError("Blueprint contains no nodes")
        self.current_node_id = nodes[0]["id"]

    def record_node_result(self, result: NodeResult, node_type: NodeType) -> None:
        """Record a completed node and advance according to edges + policy."""
        self.sequence += 1
        # Placeholder for the real transition logic
        pass

    def assert_no_third_ci_round(self) -> None:
        """Explicit guard used by tests and by the engine before any CI node."""
        if self.policy.ci_rounds >= self.policy.max_ci_rounds:
            raise RuntimeError(
                "Hard stop: second CI round has already completed. "
                "Control must be handed to a human (see AGENTS.md §2)."
            )
