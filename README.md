# Specialized Agentic Harness

**Authoritative coding-agent harness — deterministic governance of probabilistic generation**

This repository provides a reusable, model-agnostic specialized agentic harness. Its purpose is to ensure that only repository-conformant, independently verified changes can cross the boundary from model-generated proposal to accepted implementation, while keeping latency, cost, complexity, and new failure surface to the minimum sufficient level.

The coding model is not the authority. The repository, specifications, invariants, tests, policies, and acceptance rules are the authority. The harness exists to enforce that boundary.

## Authority Documents

| Document | Purpose |
|----------|---------|
| [AGENTS.md](AGENTS.md) | Primary behavioral contract, five questions, and invariants |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design as authoritative governor |
| [CONSTRAINTS.md](CONSTRAINTS.md) | Hard limits and non-negotiable policies |
| [BLUEPRINTS.md](BLUEPRINTS.md) | Blueprint schema and required workflows |
| [OBSERVABILITY.md](OBSERVABILITY.md) | Trajectories, metrics, and evaluation |
| [SECURITY.md](SECURITY.md) | Isolation, permissions, and threat model |

These documents are the source of truth. Runtime code must enforce them.

## Core Properties

- **Authoritative governance**: resolve → constrain → execute → verify → decide
- **Independent declaration of success**: the model that wrote the code does not get to declare completion
- **Hybrid control**: Agentic nodes propose within bounds; deterministic nodes enforce authority, constraints, and verification
- **Hard limits**: at most two CI rounds; ≤ 1,000 net LOC per sprint; isolation boundary
- **Model-agnostic**: any model that supports tool calling can be used
- **Minimum sufficient control surface**: every control must earn its place
- **Full trajectory**: every node emits structured, content-addressed evidence

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
├── AGENTS.md, ARCHITECTURE.md, CONSTRAINTS.md, ...
├── blueprints/               # Concrete blueprint definitions
├── src/specialized_harness/  # Engine, nodes, sandboxes, policy
├── configs/                  # Monorepo overlays
├── tests/                    # Unit, integration, blueprint regression
└── docs/
```

## Design Intent

This harness is intended for organizations that already possess strong local verification, selective CI, and a culture of human review when residual judgment is required. It does not attempt to replace human review as the final merge gate; it produces a process-compliant, independently verified change (or an explicit handoff) that is ready for that review.

The reliability guarantees come from authority resolution, constraint, deterministic verification, and independent decision — not from the model.

## License

Apache-2.0
