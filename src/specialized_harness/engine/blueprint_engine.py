"""Blueprint Engine - state machine that owns phase transitions.

Embodies AGENTS.md / CONSTRAINTS.md: refuses illegal transitions,
especially any attempt to exceed max_ci_rounds.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4

from specialized_harness.engine.models import (
    ExitStatus,
    FinalStatus,
    NodeResult,
    NodeType,
    PolicyState,
    RunResult,
    TrajectoryEvent,
)
from specialized_harness.policy.enforcer import PolicyEnforcer


Handler = Callable[[dict[str, Any]], NodeResult]


class BlueprintEngine:
    def __init__(
        self,
        blueprint: dict[str, Any],
        handlers: dict[str, Handler],
        run_id: str | None = None,
        context: dict[str, Any] | None = None,
    ):
        self.blueprint = blueprint
        self.handlers = handlers
        self.run_id = run_id or str(uuid4())
        self.context = context or {}
        policy_cfg = blueprint.get("spec", {}).get("policy", {})
        self.policy = PolicyState(
            max_ci_rounds=int(policy_cfg.get("max_ci_rounds", 2)),
            max_agentic_recovery_attempts=int(
                policy_cfg.get("max_agentic_recovery_attempts", 1)
            ),
            max_net_loc=int(policy_cfg.get("max_net_loc", 1000)),
        )
        if self.policy.max_ci_rounds > 2:
            raise ValueError("Hard constraint: max_ci_rounds cannot exceed 2")
        self.enforcer = PolicyEnforcer(self.policy)
        self.trajectory: list[TrajectoryEvent] = []
        self.nodes_by_id = {n["id"]: n for n in blueprint["spec"]["nodes"]}
        self.edges = blueprint["spec"]["edges"]
        self.current_node_id: str | None = None
        self.sequence = 0
        self.final_status = FinalStatus.RUNNING

    def start(self) -> None:
        nodes = self.blueprint["spec"]["nodes"]
        if not nodes:
            raise ValueError("Blueprint contains no nodes")
        self.current_node_id = nodes[0]["id"]

    def run(self) -> RunResult:
        self.start()
        safety = 0
        while self.current_node_id and self.final_status == FinalStatus.RUNNING:
            safety += 1
            if safety > 50:
                self.final_status = FinalStatus.FAILED
                return RunResult(
                    self.run_id, self.final_status, self.trajectory, "safety limit"
                )
            node = self.nodes_by_id[self.current_node_id]
            result = self._execute_node(node)
            nxt = self._next_node(node["id"], result)
            if nxt is None:
                if node["id"] == "decide" or node.get("handler") == "decide_accept_or_handoff":
                    status = result.metadata.get("final_status", FinalStatus.FAILED.value)
                    self.final_status = FinalStatus(status)
                elif result.status == ExitStatus.SUCCESS:
                    self.final_status = FinalStatus.ACCEPT
                else:
                    self.final_status = FinalStatus.FAILED
                break
            self.current_node_id = nxt
        return RunResult(self.run_id, self.final_status, self.trajectory)

    def _execute_node(self, node: dict[str, Any]) -> NodeResult:
        node_id = node["id"]
        node_type = NodeType(node["type"])
        handler_name = node.get("handler", node_id)

        if node_id == "ci_round" or handler_name in (
            "selective_ci",
            "selective_ci_and_verify_outcome",
        ):
            self.enforcer.check_ci_round_allowed()
            self.policy.record_ci_round()

        started = datetime.now(timezone.utc).isoformat()
        handler = self.handlers.get(handler_name) or self.handlers.get(node_id)
        if handler is None:
            result = NodeResult(
                ExitStatus.FAILURE, error=f"No handler registered for {handler_name}"
            )
        else:
            ctx = {
                **self.context,
                "node": node,
                "policy": self.policy,
                "run_id": self.run_id,
            }
            result = handler(ctx)
        finished = datetime.now(timezone.utc).isoformat()

        self.sequence += 1
        event = TrajectoryEvent(
            run_id=self.run_id,
            node_id=node_id,
            node_type=node_type,
            sequence=self.sequence,
            started_at=started,
            finished_at=finished,
            exit_status=result.status,
            ci_round=self.policy.ci_rounds,
            recovery_attempt=self.policy.recovery_attempts,
            token_usage=result.metadata.get("token_usage", {}),
            tools_called=result.metadata.get("tools_called", []),
            artifacts=result.artifacts,
            error=result.error,
            metadata=result.metadata,
        )
        self.trajectory.append(event)
        return result

    def _eval_when(self, expr: str) -> bool:
        env = {
            "ci_rounds": self.policy.ci_rounds,
            "max_ci_rounds": self.policy.max_ci_rounds,
            "recovery_attempts": self.policy.recovery_attempts,
            "max_agentic_recovery_attempts": self.policy.max_agentic_recovery_attempts,
            "net_loc": self.policy.net_loc,
            "max_net_loc": self.policy.max_net_loc,
        }
        try:
            return bool(eval(expr, {"__builtins__": {}}, env))  # noqa: S307
        except Exception:
            return False

    def _next_node(self, from_id: str, result: NodeResult) -> str | None:
        on = "success" if result.status == ExitStatus.SUCCESS else "failure"

        def edge_on(e: dict) -> str | None:
            # PyYAML 1.1 may parse bare key `on` as boolean True
            if "on" in e:
                return e["on"]
            if True in e:
                return e[True]
            if "on_status" in e:
                return e["on_status"]
            return None

        candidates = [e for e in self.edges if e["from"] == from_id and edge_on(e) == on]
        for edge in candidates:
            when = edge.get("when")
            if when is None or self._eval_when(when):
                if from_id in ("local_verify", "local_lint") and on == "failure":
                    if self.policy.can_recover():
                        self.policy.record_recovery()
                return edge["to"]
        return None

    def assert_no_third_ci_round(self) -> None:
        self.enforcer.check_ci_round_allowed()
