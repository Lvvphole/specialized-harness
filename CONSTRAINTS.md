# CONSTRAINTS.md — Hard Invariants & Policies

**Status**: Production Authority  
**Version**: 1.1.0  
**Authority Rank**: Second only to AGENTS.md  
**Aligned With**: AGENTS.md v1.1.0

This document enumerates the non-negotiable constraints of the Specialized Agentic Harness. Runtime code must enforce every constraint listed here. Soft preferences belong in configuration; hard limits belong here.

These constraints exist to support the five questions the harness must answer and the requirement that only repository-conformant, independently verified changes may be accepted.

---

## 1. Authority & Scope Limits

| Constraint | Value / Rule | Enforcement |
|------------|--------------|-------------|
| Authority must be resolved before execution | Task contract, applicable specs, tests, policies, and repository constraints must be deterministically established | Engine blocks run start if authority is ambiguous or missing |
| Model cannot redefine requirements | The agent may not expand, reinterpret, or override the task contract or acceptance criteria | Policy Enforcer + trajectory audit |
| Scope is explicit and bounded | Only files, tools, and side effects declared for the current node/blueprint are permitted | Tool surface restriction + sandbox isolation |
| Net LOC per sprint/run | ≤ 1,000 lines of code | Diff measurement before finalize; excess forces human handoff or rejection |

---

## 2. Iteration & Feedback Limits

| Constraint | Value | Enforcement |
|------------|-------|-------------|
| Maximum CI rounds per run | 2 | Policy Enforcer refuses transition to a third CI node |
| Maximum agentic recovery attempts after local lint failure | 1 (configurable per blueprint, hard ceiling 2) | Engine counter |
| Maximum wall-clock time per agentic node | Defined in blueprint (default 15 min) | Runtime timeout |
| Maximum total tokens per run | Defined in blueprint + global ceiling | Token budget tracker |

After the second CI round completes (success or failure), the engine must transition to either acceptance (if all required evidence is present) or human handoff. No further agentic nodes are permitted.

---

## 3. Isolation & Security

- All agent execution occurs inside a disposable sandbox (devbox).
- The sandbox must have no network route to production systems or the public internet (except for explicitly allow-listed, read-only package mirrors if required by the monorepo build).
- Secrets and credentials that grant production access must never be injected into the sandbox.
- The agent receives full local permissions (filesystem, process, and package install) inside the sandbox and zero permissions outside it.
- Sandbox teardown is mandatory at the end of every run (success, failure, or timeout).

---

## 4. Deterministic Gate Integrity

- Every deterministic node listed in a blueprint must execute when its turn arrives.
- The model is never given the ability to skip, reorder, or mark a deterministic node as optional.
- Results of deterministic nodes (lint status, test results, type-check, contract validation, git status) are authoritative. Model statements that contradict them are ignored for control-flow purposes.
- Autofixes, when available, are applied by deterministic code before control is returned to an agentic node.
- Outcome verification must measure the desired state, not merely “command exited 0” or “code was produced.”

---

## 5. Context & Tool Scoping

- Agent rule files are applied conditionally (by directory, path pattern, or explicit blueprint parameter). Global unconditional rules that apply to an entire large monorepo are prohibited.
- Each agentic node receives only the tool surface declared for that node. The full tool catalog is never presented.
- Tool results that exceed a size threshold must be summarized or truncated before being re-injected into the model context.
- The model cannot expand its own tool surface or permissions.

---

## 6. Trajectory & Observability Requirements

- Every node execution must produce a structured trajectory event containing at minimum:
  - node_id
  - node_type (agentic | deterministic)
  - start_ts / end_ts
  - exit_status
  - token_usage (if agentic)
  - artifacts produced or modified
  - evidence references (tests run, checks performed, authority sources used)
- Incomplete trajectories are treated as infrastructure failures and cause the run to be marked failed.
- Trajectories are immutable once written.
- Rejection of unsupported claims of completion must be recorded with the reason.

---

## 7. Definition of Done Enforcement

A run may be marked complete only when one of the following is true:

1. The harness has independently verified that the required outcome occurred and all protected invariants hold, and sufficient evidence has been emitted, or
2. A hard limit (CI rounds, LOC, recovery attempts, timeout) has been reached and an explicit human-handoff record has been emitted.

The model is not permitted to declare the run complete.  
“Code was produced” or “command exited 0” is never sufficient by itself.

---

## 8. Minimum Sufficient Control Surface

Every additional control, node, tool, policy, or observation layer must demonstrably improve:
- Correct accepted outcomes, or
- Failure containment, or
- Authority enforcement

Complexity that does not improve the harness value function is rejected. The harness itself must not become a larger failure surface than the coding task it governs.

---

## 9. Change Control for Constraints

- Adding a new hard constraint requires an update to this document and a corresponding enforcement test.
- Removing or weakening a constraint requires an explicit architectural decision record and a major version bump.
- Runtime code that can violate a constraint listed here is considered a critical defect.
- Changes must remain consistent with the five questions and independent-declaration-of-success principle in AGENTS.md.
