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

```
┌────────────────────────────────────────────────────────────────┐
│                        Invocation Surfaces                      │
│              (CLI · GitHub Action · Slack · API)                │
└───────────────────────────────┬──────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                      Blueprint Engine                           │
│   (state machine that owns phase transitions and policy state)  │
└───────────┬────────────────────────────────────┬────────────────────┘
             │                               │
             ▼                               ▼
┌───────────────────────┐     ┌───────────────────────────┐
│   Deterministic Nodes  │     │      Agentic Nodes         │
│  • resolve_authority   │     │  • plan                    │
│  • constrain_scope     │     │  • implement               │
│  • lint / type-check   │     │  • fix_ci_failures         │
│  • selective_ci        │     │                            │
│  • verify_outcome      │     │                            │
│  • policy_enforcer     │     │                            │
│  • decide_accept       │     │                            │
└───────────┬───────────┘     └───────────┬──────────────┘
             │                               │
             └──────────────┬──────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                     Execution Environment                       │
│   Devbox Manager  ·  Sandbox Isolation  ·  Trajectory Logger    │
└────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Components

### 3.1 Blueprint Engine
- Loads and validates a blueprint definition.
- Maintains phase state and policy counters (CI rounds, recovery attempts, LOC budget).
- Dispatches nodes according to edges and exit status.
- Refuses any transition that would violate AGENTS.md or CONSTRAINTS.md.

### 3.2 Deterministic Nodes
Pure (or near-pure) functions that always execute when reached, return structured results, never call a language model, and are unit-testable in isolation.

### 3.3 Agentic Nodes
Receive a restricted tool surface; may propose implementations; cannot declare success or expand authority.

### 3.4 Devbox / Sandbox Manager
Provisions isolated, disposable environments with no production network access.

### 3.5 Trajectory & Observability Layer
Every node emits a structured event; trajectories are content-addressed and immutable.

### 3.6 Policy Enforcer
Last line of defense; enforces independent declaration of success.

---

## 4. Runtime Flow (Standard Coding Blueprint)

1. Invocation — Task specification received.
2. Resolve Authority (deterministic).
3. Constrain Scope (deterministic).
4. Provision — Sandbox created.
5. Plan (agentic).
6. Implement (agentic).
7. Local Verification (deterministic).
8. Push (deterministic) — local only unless remote configured.
9. CI Round 1 (deterministic).
10. Fix CI (agentic, optional).
11. CI Round 2 (deterministic, final).
12. Decide (deterministic) — Accept or human handoff.
13. Teardown.

---

## 5. Reusability Across Monorepos

Monorepo-specific behavior is supplied through configs overlays, conditional rules, and blueprint parameters.

---

## 6. Extension Points

New nodes and blueprints must respect AGENTS.md and CONSTRAINTS.md hard invariants. Model providers are pluggable.

---

## 7. Non-Goals

- Open-ended multi-hour autonomous research without a fixed blueprint and authority resolution.
- Letting the model decide when to stop, when to run quality gates, or whether the task is complete.
- Supporting arbitrary network or production-side effects from within a run.
- Replacing human review as the final merge gate when residual judgment is required.
- Becoming a larger, slower, or more expensive failure surface than the coding task being governed.

### Harness repository governance

For **this** repository's `main` branch: human review is not residual—it is **mandatory**. LLMs and agents may propose changes only via pull request; they have **no** authority to merge or write to `main`. See AGENTS.md §8.
