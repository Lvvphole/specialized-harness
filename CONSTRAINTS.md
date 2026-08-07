# CONSTRAINTS.md — Hard Invariants & Policies

**Status**: Production Authority  
**Version**: 1.2.0  
**Authority Rank**: Second only to AGENTS.md (and GOAL.md as north star) among runtime policy documents  
**Aligned With**: AGENTS.md v1.2.0

---

## 1. Purpose

This document enumerates the non-negotiable constraints of the Specialized Agentic Harness. Runtime code must enforce every constraint listed here. Soft preferences belong in configuration; hard limits belong here.

These constraints exist to support the five questions the harness must answer and the requirement that only repository-conformant, independently verified changes may be accepted.

---

## 2. Hard constraints (summary)

| Constraint | Rule | Typical enforcement |
|------------|------|---------------------|
| Authority must be resolved before execution | Task contract, specs, tests, policies established | `resolve_authority` blocking |
| Scope is explicit and bounded | Only authorized files/tools/side effects | Sandbox + tool surface |
| Deterministic gates cannot be skipped | Model cannot reorder or disable gates | Blueprint engine |
| max_ci_rounds ≤ 2 | After second CI failure, human handoff | PolicyEnforcer |
| max_net_loc ≤ 1000 | Sprint/run size limit | PolicyEnforcer + measure_net_loc |
| Model does not declare success | Completion only via checks or human handoff | Evidence ledger + decide |
| Trajectory required | Incomplete trajectory = infrastructure failure | Engine + observability |
| Isolation | Disposable sandbox; no production network | WorkspaceSandbox |
| **PRs required for `main`** | No LLM/agent commit, push, or merge to `main` | Branch protection + process |
| **Human-only merge to `main`** | Only human reviewer merges to `main` | AGENTS.md §8 + GitHub settings |

---

## 3. Isolation

- All agent execution occurs inside a disposable sandbox (devbox).
- The sandbox must have no network route to production systems or the public internet (except explicitly allow-listed, read-only package mirrors if required).
- Secrets and credentials that grant production access must never be injected into the sandbox.
- The agent receives full local permissions inside the sandbox and zero permissions outside it.

---

## 4. Iteration and cost bounds

- At most **two** CI rounds per run. After the second CI round, control is surrendered; no further agentic work on that run.
- Recovery attempts are strictly budgeted (default: one agentic recovery path where the blueprint allows).
- Net lines of code changed in a single sprint/run must not exceed **1,000**.

---

## 5. Trajectory and evidence

- Every node execution must emit a structured trajectory record.
- Incomplete trajectories are treated as infrastructure failures and cause the run to be marked failed.
- Trajectories are immutable once written.
- Rejection of unsupported claims of completion must be recorded with the reason.

---

## 6. Definition of Done Enforcement

A run may be marked complete only when one of the following is true:

1. The harness has independently verified that the required outcome occurred and all protected invariants hold, and sufficient evidence has been emitted, or
2. A hard limit (CI rounds, LOC, recovery attempts, timeout) has been reached and an explicit human-handoff record has been emitted.

The model is not permitted to declare the run complete.  
“Code was produced” or “command exited 0” is never sufficient by itself.

---

## 7. Minimum Sufficient Control Surface

Every additional control, node, tool, policy, or observation layer must demonstrably improve:
- Correct accepted outcomes, or
- Failure containment, or
- Authority enforcement

Complexity that does not improve the harness value function is rejected.

---

## Repository governance (`main`)

Hard constraint for **this repository** (not for sandboxed task runs):

| Constraint | Rule | Enforcement |
|------------|------|-------------|
| Pull requests required for `main` | No LLM, coding agent, or automated bot may commit, push, or merge to `main` | Branch protection + human review |
| Human-only merge | Only a human reviewer (repository owner or designated human) may merge to `main` or authorize a direct write to `main` | GitHub settings + AGENTS.md §8 |
| Agent proposals | Models may open PRs from feature branches only; they must not self-merge | Process + protection rules |

Violating this constraint is treated as a governance defect of the same severity as disabling a quality gate.

---

## Change Control for Constraints

- Adding a new hard constraint requires an update to this document and a corresponding enforcement test where applicable.
- Removing or weakening a constraint requires an explicit architectural decision record and a major version bump.
- Runtime code that can violate a constraint listed here is considered a critical defect.
- Changes must remain consistent with the five questions and independent-declaration-of-success principle in AGENTS.md.
- Updates ship only via **pull request**; **human** merge to `main` only (AGENTS.md §8).
