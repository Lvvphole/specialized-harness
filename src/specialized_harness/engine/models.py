"""Shared runtime models for the blueprint engine."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NodeType(str, Enum):
    DETERMINISTIC = "deterministic"
    AGENTIC = "agentic"


class ExitStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class FinalStatus(str, Enum):
    ACCEPT = "ACCEPT"
    HUMAN_HANDOFF = "HUMAN_HANDOFF"
    FAILED = "FAILED"
    RUNNING = "RUNNING"


@dataclass
class NodeResult:
    status: ExitStatus
    artifacts: list[str] = field(default_factory=list)
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyState:
    ci_rounds: int = 0
    recovery_attempts: int = 0
    max_ci_rounds: int = 2
    max_agentic_recovery_attempts: int = 1
    net_loc: int = 0
    max_net_loc: int = 1000

    def can_start_ci_round(self) -> bool:
        return self.ci_rounds < self.max_ci_rounds

    def record_ci_round(self) -> None:
        if not self.can_start_ci_round():
            raise RuntimeError("Policy violation: CI round beyond max_ci_rounds")
        self.ci_rounds += 1

    def can_recover(self) -> bool:
        return self.recovery_attempts < self.max_agentic_recovery_attempts

    def record_recovery(self) -> None:
        if not self.can_recover():
            raise RuntimeError("Policy violation: recovery attempts exhausted")
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
    token_usage: dict[str, int]
    tools_called: list[str]
    artifacts: list[str]
    error: str | None
    metadata: dict[str, Any]
    duration_ms: int = 0


@dataclass
class RunResult:
    run_id: str
    final_status: FinalStatus
    trajectory: list[TrajectoryEvent]
    error: str | None = None
    total_ms: int = 0
