# CONSTRAINTS.md — Hard Invariants & Policies

**Status**: Production Authority  
**Version**: 1.2.0  
**Authority Rank**: Parallel to VERIFICATION.md / ECONOMICS.md / OBSERVABILITY.md; subordinate only to AGENTS.md and GOAL.md  
**Aligned With**: AGENTS.md v1.2.0

---

## 1. Purpose

This document enumerates the non-negotiable constraints of the Specialized Agentic Harness. Runtime code must enforce every constraint listed here. Soft preferences belong in configuration; hard limits belong here.

These constraints exist to support the five questions the harness must answer and the requirement that only repository-conformant, independently verified changes may be accepted.

---

## 2. Summary table (selected)

| Constraint | Intent |
|------------|--------|
| Authority must be resolved before execution | Blocking if missing |
| Scope is explicit and bounded | Sandbox + tool surface |
| max_ci_rounds ≤ 2 | Human handoff after second failure |
| max_net_loc ≤ 1000 | Sprint/run size limit |
| Model does not declare success | Ledger + decide |
| **Pull requests required for `main`** | No LLM commit/push/merge to `main` |
| **Human-only merge to `main`** | Only human reviewer merges |

---

## 3–8. Runtime constraints

(See full historical sections in repository history for isolation, CI, LOC, trajectory, and DoD enforcement detail. Core runtime constraints are unchanged by v1.2.0 governance rules.)

- All agent execution occurs inside a disposable sandbox.
- At most two CI rounds per run; then human handoff.
- Net LOC per sprint/run must not exceed 1,000.
- Incomplete trajectories are infrastructure failures.
- The model is not permitted to declare the run complete.

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
