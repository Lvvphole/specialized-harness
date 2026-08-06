# OBSERVABILITY.md — Trajectories, Metrics & Evaluation

**Status**: Production Authority  
**Version**: 1.0.0

---

## 1. Trajectory Requirements

Every run produces an immutable, ordered trajectory. The trajectory is the primary artifact used for debugging, evaluation, and continuous improvement.

### Minimum Trajectory Event Schema

```json
{
  "run_id": "uuid",
  "node_id": "string",
  "node_type": "agentic | deterministic",
  "sequence": 0,
  "started_at": "ISO-8601",
  "finished_at": "ISO-8601",
  "exit_status": "success | failure | timeout | cancelled",
  "ci_round": 0,
  "recovery_attempt": 0,
  "token_usage": {
    "prompt": 0,
    "completion": 0,
    "total": 0
  },
  "tools_called": [],
  "artifacts": [],
  "error": null,
  "metadata": {}
}
```

Incomplete trajectories (missing events, missing required fields) cause the run to be marked as an infrastructure failure.

---

## 2. Core Metrics

Computed from trajectories and stored per run and aggregated over time:

| Metric | Description |
|--------|-------------|
| `one_shot_success_rate` | Fraction of runs that reach a CI-passing PR without a second CI round |
| `two_round_success_rate` | Fraction that succeed on the second CI round |
| `human_handoff_rate` | Fraction that exhaust the CI budget |
| `avg_ci_rounds` | Average number of CI rounds used on successful runs |
| `phase_failure_attribution` | Distribution of failures by node_id |
| `avg_tokens_per_successful_pr` | Cost proxy |
| `avg_wall_time_to_pr` | Latency |
| `sandbox_provision_latency` | Infrastructure health |

---

## 3. Evaluation Harness

The evaluation system consists of three layers:

### 3.1 Blueprint Regression Suite
- Fixed set of historical tasks with recorded expected outcomes.
- Executed on every change to a blueprint, node, or policy.
- Asserts final status, number of CI rounds used, and key trajectory properties.

### 3.2 Continuous Metrics Dashboard
- Live aggregation of the metrics above.
- Alerting on regressions in one-shot success rate or sudden increases in human-handoff rate.

### 3.3 Trajectory Quality Sampling
- Periodic human or LLM-as-judge review of a sample of trajectories.
- Scores: plan quality, fidelity to diagnostics, unnecessary tool use, adherence to style constraints.

---

## 4. Error Classification

Failures are classified for attribution:

- `deterministic_failure` — a deterministic node returned failure (lint, CI, git, etc.).
- `agentic_failure` — an agentic node exhausted its budget or produced invalid output.
- `policy_violation` — an attempt was made to exceed a hard limit (caught by the Policy Enforcer).
- `infrastructure_failure` — sandbox, trajectory, or engine internal error.
- `human_handoff` — second CI round failed; control surrendered correctly.

---

## 5. Hashing & Integrity

- Each trajectory is content-addressed (SHA-256 of the canonical JSON serialization).
- Blueprint definitions are hashed on load; the hash is recorded in the trajectory header.
- Any mismatch between the expected blueprint hash and the loaded definition aborts the run.

This provides an audit trail that a particular run was executed under a specific, unmodified blueprint.
