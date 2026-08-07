# ARCHITECTURE.md — Specialized Agentic Harness

**Status**: Production Authority  
**Version**: 1.1.0  
**Aligned With**: AGENTS.md v1.1.0  
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
┌─────────────────────────────────────────────────────────────────┐
│                        Invocation Surfaces                      │
│              (CLI · GitHub Action · Slack · API)                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Blueprint Engine                           │
│   (state machine that owns phase transitions and policy state)  │
└────────────┬───────────────────────────────┬────────────────────┘
             │                               │
             ▼                               ▼
┌────────────────────────┐     ┌────────────────────────────┐
│   Deterministic Nodes  │     │      Agentic Nodes         │
│  • resolve_authority   │     │  • plan                    │
│  • constrain_scope     │     │  • implement               │
│  • lint / type-check   │     │  • fix_ci_failures         │
│  • selective_ci        │     │                            │
│  • verify_outcome      │     │                            │
│  • policy_enforcer     │     │                            │
│  • decide_accept       │     │                            │
└────────────┬───────────┘     └────────────┬───────────────┘
             │                               │
             └───────────────┬───────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Execution Environment                       │
│   Devbox Manager  ·  Sandbox Isolation  ·  Trajectory Logger    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Components

### 3.1 Blueprint Engine
- Loads and validates a blueprint definition.
- Maintains phase state and policy counters (CI rounds, recovery attempts, LOC budget).
- Dispatches nodes according to edges and exit status.
- Refuses any transition that would violate AGENTS.md or CONSTRAINTS.md (including a third CI round or exceeding the 1,000 LOC limit).

### 3.2 Deterministic Nodes
Pure (or near-pure) functions that:
- Always execute when reached.
- Return structured results.
- Never call a language model.
- Are unit-testable in isolation.

Canonical set (aligned to the five questions):
- `resolve_authority` — establish task contract, applicable specs, tests, policies
- `constrain_scope` — bind files, tools, and side effects
- `run_local_linters` / `type_check` / `contract_validate`
- `selective_ci`
- `verify_outcome` — measure whether the desired state actually holds
- `policy_check` / `decide_accept_or_handoff`
- `git_push` / `create_pull_request` (only after acceptance criteria are met)

### 3.3 Agentic Nodes
- Receive a restricted tool surface, a node-specific system prompt, and current trajectory context.
- May propose implementations within the authorized scope.
- Must terminate with a structured exit status.
- Are subject to token, time, and LOC budgets.
- Cannot declare success or expand their own authority.

### 3.4 Devbox / Sandbox Manager
- Provisions isolated, disposable environments.
- Guarantees: no production network access, no production secrets, full local permissions inside the sandbox.
- Supports pre-warming.
- Mandatory teardown at end of run.

### 3.5 Trajectory & Observability Layer
- Every node emits a structured event, including evidence references.
- Trajectories are content-addressed and immutable.
- Metrics and evaluation are derived from trajectories (see OBSERVABILITY.md).

### 3.6 Policy Enforcer
- Last line of defense against constraint violations.
- Consulted before any phase transition that could violate hard limits.
- Enforces independent declaration of success: the model never gets the final say.

---

## 4. Runtime Flow (Standard Coding Blueprint)

1. **Invocation** — Task specification received.
2. **Resolve Authority** (deterministic) — Establish applicable sources of truth.
3. **Constrain Scope** (deterministic) — Bind permissions, files, tools.
4. **Provision** — Sandbox created and warmed.
5. **Plan** (agentic) — Model proposes an implementation approach within scope.
6. **Implement** (agentic) — Model proposes code changes within scope and LOC budget.
7. **Local Verification** (deterministic) — Lint, type-check, contract validation; autofixes applied where available.
8. **Push** (deterministic) — Branch created and pushed (only if local gates pass).
9. **CI Round 1** (deterministic) — Selective tests + outcome verification.
10. **Fix CI** (agentic, optional) — Only if failures remain and recovery budget remains.
11. **CI Round 2** (deterministic, final) — Last verification attempt.
12. **Decide** (deterministic) — Accept (with evidence) or human handoff.
13. **Teardown** — Sandbox destroyed.

---

## 5. Reusability Across Monorepos

Monorepo-specific behavior is supplied through:

- `configs/<monorepo>/` overlays (CI selection, lint commands, PR template, tool scopes, authority sources).
- Conditional rule files that match by directory or file pattern.
- Blueprint variants or parameters.
- Optional custom deterministic nodes registered via a plugin interface.

The core engine and the majority of nodes remain unchanged when moving to a new monorepo.

---

## 6. Extension Points

- New deterministic nodes may be added provided they remain free of model involvement and improve the value function.
- New agentic nodes may be added provided they declare an explicit tool surface and budgets and cannot declare success.
- New blueprints may be authored only if they respect the hard invariants in AGENTS.md and CONSTRAINTS.md.
- Model providers are pluggable behind a thin interface.

---

## 7. Non-Goals

- Open-ended multi-hour autonomous research or exploration without a fixed blueprint and authority resolution.
- Letting the model decide when to stop, when to run quality gates, or whether the task is complete.
- Supporting arbitrary network or production-side effects from within a run.
- Replacing human review as the final merge gate when residual judgment is required.
- Becoming a larger, slower, or more expensive failure surface than the coding task being governed.
