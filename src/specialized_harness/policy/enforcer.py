"""Policy Enforcer — last line of defense against constraint violations."""
from __future__ import annotations

from specialized_harness.engine.models import PolicyState


class PolicyViolation(Exception):
    """Raised when a hard constraint is about to be broken."""


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

    def check_loc_allowed(self, net_loc: int) -> None:
        if net_loc > self.policy.max_net_loc:
            raise PolicyViolation(
                f"Net LOC {net_loc} exceeds max_net_loc={self.policy.max_net_loc}."
            )

    def require_trajectory_complete(self, event_count: int, expected_min: int) -> None:
        if event_count < expected_min:
            raise PolicyViolation(
                "Incomplete trajectory detected. "
                "Every node must emit a structured event (OBSERVABILITY.md)."
            )

    def check_tool_rounds_config(self) -> None:
        """Validate max_tool_rounds is a positive independent bound."""
        n = int(self.policy.max_tool_rounds)
        if n < 1:
            raise PolicyViolation("max_tool_rounds must be >= 1")
