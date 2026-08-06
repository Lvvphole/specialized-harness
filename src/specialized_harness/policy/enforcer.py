"""
Policy Enforcer — last line of defense against constraint violations.

This component is consulted before any phase transition that could
violate the hard limits in CONSTRAINTS.md and AGENTS.md.
"""

from __future__ import annotations

from typing import Optional
from specialized_harness.engine.blueprint_engine import PolicyState


class PolicyViolation(Exception):
    """Raised when a hard constraint is about to be broken."""
    pass


class PolicyEnforcer:
    def __init__(self, policy: PolicyState):
        self.policy = policy

    def check_ci_round_allowed(self) -> None:
        if not self.policy.can_start_ci_round():
            raise PolicyViolation(
                f"CI round limit exceeded (max={self.policy.max_ci_rounds}). "
                "Agent must stop and hand off to a human."
            )

    def check_recovery_allowed(self) -> None:
        if not self.policy.can_recover():
            raise PolicyViolation(
                f"Recovery attempt limit exceeded "
                f"(max={self.policy.max_agentic_recovery_attempts})."
            )

    def require_trajectory_complete(self, event_count: int, expected_min: int) -> None:
        if event_count < expected_min:
            raise PolicyViolation(
                "Incomplete trajectory detected. "
                "Every node must emit a structured event (OBSERVABILITY.md)."
            )
