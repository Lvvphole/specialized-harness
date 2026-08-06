# Specialized Agentic Harness

**Production-ready deterministic-blueprint coding harness**  
Modeled on the architecture of Stripe’s Minions system.

This repository provides a reusable, model-agnostic specialized agentic harness for one-shot, end-to-end coding tasks across monorepos. Critical quality gates are enforced by deterministic code; the language model is confined to designated creative phases.

## Authority Documents

| Document | Purpose |
|----------|---------|
| [AGENTS.md](AGENTS.md) | Primary behavioral contract and invariants |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design and component responsibilities |
| [CONSTRAINTS.md](CONSTRAINTS.md) | Hard limits and non-negotiable policies |
| [BLUEPRINTS.md](BLUEPRINTS.md) | Blueprint schema and required workflows |
| [OBSERVABILITY.md](OBSERVABILITY.md) | Trajectories, metrics, and evaluation |
| [SECURITY.md](SECURITY.md) | Isolation, permissions, and threat model |

These documents are the source of truth. Runtime code must enforce them.

## Core Properties

- **Hybrid control**: Agentic nodes for planning and implementation; deterministic nodes for lint, selective CI, git, and PR creation.
- **Hard CI limit**: At most two CI rounds. After the second round the agent stops.
- **Sandbox isolation**: Disposable environments with no production or public-network access.
- **Model-agnostic**: Any model that supports tool calling can be used.
- **Monorepo reusable**: Configuration and conditional rules adapt the harness to different codebases without changing the engine.
- **Full trajectory**: Every node emits structured, content-addressed records for audit and improvement.

## Quick Start (Conceptual)

```bash
# Install
pip install -e .

# Run a standard coding task against a repository
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

This harness is intended for organizations that already possess strong local linting, selective CI, and a culture of human review. It does not attempt to replace human judgment on the final merge; it produces a high-quality, process-compliant pull request that is ready for that review.

The reliability guarantees come from the blueprint engine and the deterministic nodes, not from the model.

## License

Apache-2.0
