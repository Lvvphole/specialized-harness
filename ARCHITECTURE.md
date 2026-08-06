# ARCHITECTURE.md — Specialized Agentic Harness

**Status**: Production Authority  
**Version**: 1.0.0  
**Modeled On**: Stripe Minions / Blueprints hybrid architecture

---

## 1. Design Philosophy

This harness implements a **hybrid control plane**:

- **Agentic nodes** provide the creative capacity of a language model (planning, implementation, interpreting failure diagnostics).
- **Deterministic nodes** provide the reliability of ordinary code (linting, selective CI, git operations, PR creation, policy enforcement).

The model never decides whether a required engineering step occurs. The blueprint decides. This separation is the primary reliability mechanism.

The system is designed for reuse across multiple monorepos. Monorepo-specific behavior is supplied through configuration, conditional rule files, and blueprint overlays rather than hard-coded assumptions about a particular codebase.

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
│         (state machine that owns phase transitions)             │
└────────────┬───────────────────────────────┬────────────────────┘
             │                               │
             ▼                               ▼
┌────────────────────────┐     ┌────────────────────────────┐
│   Deterministic Nodes  │     │      Agentic Nodes         │
│  • lint                │     │  • plan                    │
│  • selective_ci        │     │  • implement               │
│  • git_ops             │     │  • fix_ci_failures         │
│  • pr_creator          │     │  • local_fix (optional)   │
│  • policy_enforcer     │     │                            │
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
- Loads a blueprint definition (YAML or equivalent structured format).
- Maintains the current phase and a set of policy counters (most importantly the CI-round counter).
- Dispatches the next node according to the blueprint’s edges and the exit status of the previous node.
- Refuses illegal transitions (for example, attempting a third CI round).

### 3.2 Deterministic Nodes
Pure functions (or near-pure with controlled side effects) that:
- Always execute when reached.
- Return a structured result (`success`, `failure`, `autofix_applied`, etc.).
- Never call a language model.
- Are unit-testable in isolation.

Canonical set:
- `provision_sandbox`
- `hydrate_context`
- `run_local_linters`
- `git_push`
- `selective_ci`
- `apply_autofixes`
- `create_pull_request`
- `policy_check`

### 3.3 Agentic Nodes
- Receive a restricted tool surface, a node-specific system prompt, and the current trajectory context.
- May call tools, reason, and produce code changes.
- Must terminate with a structured exit status that the engine can interpret.
- Are subject to token and time budgets defined in the blueprint.

### 3.4 Devbox / Sandbox Manager
- Provisions isolated, disposable environments (container or VM based).
- Guarantees: no network egress to production, no access to secrets outside the sandbox, full local filesystem and process permissions inside the sandbox.
- Supports pre-warming for low spin-up latency.
- Tears down the environment after the run (or on failure).

### 3.5 Trajectory & Observability Layer
- Every node emits a structured event.
- The complete ordered trajectory is persisted and attached to the final PR or handoff record.
- Metrics (success rate, CI rounds used, phase-level failure attribution, cost) are computed from trajectories.

### 3.6 Policy Enforcer
- Holds the hard limits defined in CONSTRAINTS.md and AGENTS.md.
- Is consulted before any phase transition that could violate a limit.
- Is the last line of defense against runaway agent behavior.

---

## 4. Runtime Flow (Standard Coding Blueprint)

1. **Invocation** — Task specification + repository context received.
2. **Provision** — Sandbox created and warmed.
3. **Hydrate** — Conditional rules attached; selected MCP/tools pre-executed for context.
4. **Plan** (agentic) — Model produces an implementation plan.
5. **Implement** (agentic) — Model writes code under restricted tools.
6. **Local Lint** (deterministic) — Configured linters run; autofixes applied if available.
7. **Push** (deterministic) — Branch created and pushed.
8. **CI Round 1** (deterministic) — Selective tests executed; autofixes applied.
9. **Fix CI** (agentic, optional) — Only if failures remain after autofix.
10. **CI Round 2** (deterministic, final) — Second and last CI attempt.
11. **Finalize** (deterministic) — PR created or human-handoff record emitted.
12. **Teardown** — Sandbox destroyed.

---

## 5. Reusability Across Monorepos

Monorepo-specific behavior is supplied through:

- `configs/<monorepo>/` overlays (CI selection rules, lint commands, PR template, tool scopes).
- Conditional rule files under `rules/` that match by directory or file pattern.
- Blueprint variants or parameters (e.g., different test selection strategies).
- Optional custom deterministic nodes registered via a plugin interface.

The core engine and the majority of nodes remain unchanged when moving to a new monorepo.

---

## 6. Extension Points

- New deterministic nodes may be added provided they remain pure with respect to model involvement.
- New agentic nodes may be added provided they declare their tool surface and budgets.
- New blueprints may be authored as long as they respect the hard invariants in AGENTS.md and CONSTRAINTS.md.
- Model providers are pluggable behind a thin interface that normalizes tool calling and structured output.

---

## 7. Non-Goals

- Open-ended multi-hour autonomous research or exploration without a fixed blueprint.
- Letting the model decide when to stop or when to run quality gates.
- Supporting arbitrary network or production-side effects from within a run.
- Replacing human review as the final merge gate.
