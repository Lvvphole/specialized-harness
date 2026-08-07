# ARCHITECTURE.md — Specialized Agentic Harness

**Status**: Production Authority  
**Version**: 1.2.0  
**Aligned With**: AGENTS.md v1.2.0  
**Modeled On**: Deterministic governance patterns (including hybrid control as used in production systems such as Stripe Minions / Blueprints)

---

## 1. Design Philosophy

This harness is an **authoritative governor** around a probabilistic coding model.

Its purpose is not to make the model smarter. Its purpose is to ensure that only repository-conformant, independently verified changes can cross the boundary from model-generated proposal to accepted implementation, while keeping latency, cost, complexity, and new failure surface to the minimum sufficient level.

The architectural separation is:

```text
AUTHORITATIVE SOURCES
repo + specs + tests + policies + task contract
              │
              ▼
        HARNESS / GOVERNOR
resolve → constrain → execute → verify → decide
              │
              ▼
        CODING MODEL
     proposes implementation
              │
              ▼
        REPOSITORY CHANGE
              │
              ▼
      INDEPENDENT EVIDENCE
 tests + static checks + diff + runtime evidence
              │
              ▼
       ACCEPT / REJECT
```

### Hybrid Control Plane

- **Agentic nodes** supply the generative capacity of a language model (proposing plans and implementations within bounded scope).
- **Deterministic nodes** supply the reliability of ordinary code (authority resolution, constraint enforcement, verification, policy decisions, and independent declaration of success).

The model never decides whether a required engineering step occurs, whether an invariant holds, or whether the task is complete. The harness decides.

---

## 2. High-Level Component Diagram

(See prior revisions for full ASCII diagram; structure unchanged.)

---

## 3. Core Components

Blueprint Engine, Deterministic Nodes, Agentic Nodes, Sandbox Manager, Trajectory layer, and Policy Enforcer — as defined in AGENTS.md and CONSTRAINTS.md. Unchanged by repository governance rules except as noted in §7.

---

## 4. Runtime Flow (Standard Coding Blueprint)

resolve_authority → constrain_scope → provision → plan → implement → local_verify → push → ci_round → (fix_ci) → decide → teardown

---

## 5. Reusability Across Monorepos

Monorepo-specific behavior is supplied through configs overlays, conditional rules, and blueprint parameters.

---

## 6. Extension Points

New nodes and blueprints must respect AGENTS.md and CONSTRAINTS.md hard invariants.

---

## 7. Non-Goals

- Open-ended multi-hour autonomous research without a fixed blueprint and authority resolution.
- Letting the model decide when to stop, when to run quality gates, or whether the task is complete.
- Supporting arbitrary network or production-side effects from within a run.
- Replacing human review as the final merge gate when residual judgment is required.
- Becoming a larger, slower, or more expensive failure surface than the coding task being governed.

### Harness repository governance

For **this** repository's `main` branch: human review is not residual—it is **mandatory**. LLMs and agents may propose changes only via pull request; they have **no** authority to merge or write to `main`. See AGENTS.md §8.
