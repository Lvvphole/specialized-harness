# CONSTRAINTS.md — Hard Invariants & Policies

**Status**: Production Authority  
**Version**: 1.0.0  
**Authority Rank**: Second only to AGENTS.md

This document enumerates the non-negotiable constraints of the Specialized Agentic Harness. Runtime code must enforce every constraint listed here. Soft preferences belong in configuration; hard limits belong here.

---

## 1. Iteration & Feedback Limits

| Constraint | Value | Enforcement |
|------------|-------|-------------|
| Maximum CI rounds per run | 2 | Policy Enforcer refuses transition to a third CI node |
| Maximum agentic recovery attempts after local lint failure | 1 (configurable per blueprint, hard ceiling 2) | Engine counter |
| Maximum wall-clock time per agentic node | Defined in blueprint (default 15 min) | Runtime timeout |
| Maximum total tokens per run | Defined in blueprint + global ceiling | Token budget tracker |

After the second CI round completes (success or failure), the engine must transition to either `create_pull_request` or `human_handoff`. No further agentic nodes are permitted.

---

## 2. Isolation & Security

- All agent execution occurs inside a disposable sandbox (devbox).
- The sandbox must have no network route to production systems or the public internet (except for explicitly allow-listed, read-only package mirrors if required by the monorepo build).
- Secrets and credentials that grant production access must never be injected into the sandbox.
- The agent receives full local permissions (filesystem, process, and package install) inside the sandbox and zero permissions outside it.
- Sandbox teardown is mandatory at the end of every run (success, failure, or timeout).

---

## 3. Deterministic Gate Integrity

- Every deterministic node listed in a blueprint must execute when its turn arrives.
- The model is never given the ability to skip, reorder, or mark a deterministic node as optional.
- Results of deterministic nodes (lint status, test results, git status) are authoritative. Model statements that contradict them are ignored for control-flow purposes.
- Autofixes, when available, are applied by deterministic code before control is returned to an agentic node.

---

## 4. Context & Tool Scoping

- Agent rule files are applied conditionally (by directory, path pattern, or explicit blueprint parameter). Global unconditional rules that apply to an entire large monorepo are prohibited.
- Each agentic node receives only the tool surface declared for that node. The full tool catalog is never presented.
- Tool results that exceed a size threshold must be summarized or truncated before being re-injected into the model context.

---

## 5. Trajectory & Observability Requirements

- Every node execution must produce a structured trajectory event containing at minimum:
  - node_id
  - node_type (agentic | deterministic)
  - start_ts / end_ts
  - exit_status
  - token_usage (if agentic)
  - artifacts produced or modified
- Incomplete trajectories are treated as infrastructure failures and cause the run to be marked failed.
- Trajectories are immutable once written.

---

## 6. Definition of Done Enforcement

A run may be marked complete only when one of the following is true:

1. A pull request has been created and the required local + CI gates have passed, or
2. The second CI round has failed and a human-handoff record has been emitted.

The model is not permitted to declare the run complete.

---

## 7. Change Control for Constraints

- Adding a new hard constraint requires an update to this document and a corresponding enforcement test.
- Removing or weakening a constraint requires an explicit architectural decision record and a major version bump.
- Runtime code that can violate a constraint listed here is considered a critical defect.
