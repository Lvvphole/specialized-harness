# Specialized Agentic Harness

**Authoritative coding-agent harness — deterministic governance of probabilistic generation**

This repository provides a reusable, model-agnostic specialized agentic harness. Its purpose is to ensure that only repository-conformant, independently verified changes can cross the boundary from model-generated proposal to accepted implementation, while keeping latency, cost, complexity, and new failure surface to the minimum sufficient level.

The coding model is not the authority. The repository, specifications, invariants, tests, policies, and acceptance rules are the authority. The harness exists to enforce that boundary.

## The Four Pillars

| Layer | Fundamental question | Goal |
|-------|----------------------|------|
| **Authoritative** | What must be true? | Define correctness, constraints, permissions, and acceptance |
| **Verifier** | How do we know it is true? | Produce sufficient repository-aware evidence |
| **Economics** | What is the least costly sufficient way to establish and sustain it? | Optimize total cost of correctness under mandatory floors |
| **Observability** | How is the system performing over time? | Measure, attribute drift, and make adaptation empirical |

**Authority defines truth. Verification establishes truth. Economics determines the minimum sufficient cost of establishing truth. Observability tells us whether the system is consistently delivering it.**

## Authority Documents

| Document | Purpose |
|----------|---------|
| [AGENTS.md](AGENTS.md) | Primary behavioral contract, five questions, and invariants |
| [CONSTRAINTS.md](CONSTRAINTS.md) | Hard limits and non-negotiable policies |
| [VERIFICATION.md](VERIFICATION.md) | Repository-aware hybrid verifier (three loops) |
| [ECONOMICS.md](ECONOMICS.md) | Total cost of correctness, Minimum Sufficient Harness Principle |
| [OBSERVABILITY.md](OBSERVABILITY.md) | Trajectories, evals, metrics, drift, adaptation |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design as authoritative governor |
| [BLUEPRINTS.md](BLUEPRINTS.md) | Blueprint schema and required workflows |
| [SECURITY.md](SECURITY.md) | Isolation, permissions, and threat model |

These documents are the source of truth. Runtime code must enforce them.

## Core Properties

- **Authoritative governance**: resolve → constrain → execute → verify → decide
- **Independent declaration of success**: the model that wrote the code does not get to declare completion
- **Hybrid verification**: algorithmic checks + bounded agentic review under an explicit verification contract
- **Three verification loops**: Agentic (semantic), CI (executable), Maintenance (repository health over time)
- **Minimum Sufficient Harness**: every control must earn its place; cheapest sufficient path is selected at runtime
- **Observability-driven adaptation**: trajectories + evals make control admission and removal empirical
- **Hard limits**: at most two CI rounds; ≤ 1,000 net LOC per sprint; isolation boundary
- **Model-agnostic**: any model that supports tool calling can be used; model selection is economically governed
- **Full trajectory + Evidence Ledger**: every node and every claim is inspectable

## The Five Questions the Harness Must Answer

1. What is actually required?
2. What is the agent allowed to change?
3. Did the implementation preserve the system’s invariants?
4. Did the requested outcome actually occur?
5. Who gets to declare success?

## Quick Start (Conceptual)

```bash
# Install
pip install -e .

# Run a governed coding task
specialized-harness run \
  --blueprint standard-coding \
  --repo /path/to/monorepo \
  --task "Fix the flaky test in payments/invoice_test.rb" \
  --model <provider/model>
```

## Repository Layout

```
specialized-harness/
├── AGENTS.md, CONSTRAINTS.md, VERIFICATION.md, ECONOMICS.md, OBSERVABILITY.md, ...
├── blueprints/               # Concrete blueprint definitions
├── src/specialized_harness/  # Engine, nodes, sandboxes, policy, verifier, economics, observability
├── configs/                  # Monorepo overlays
├── tests/                    # Unit, integration, blueprint regression
└── docs/
```

## Design Intent

This harness is intended for organizations that already possess strong local verification, selective CI, and a culture of human review when residual judgment is required. It does not attempt to replace human review as the final merge gate; it produces a process-compliant, independently verified change (or an explicit handoff) that is ready for that review.

The reliability guarantees come from authority resolution, constraint, hybrid verification, independent decision, economic governance, and observability-driven adaptation — not from the model.

## License

Apache-2.0
