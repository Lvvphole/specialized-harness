# Specialized Agentic Harness

**A model-agnostic optimization system for discovering, executing, verifying, and economically selecting workflows for complex problem solving.**

> Find the cheapest sufficient workflow that can reliably solve the problem, prove that it works, and prove why it deserves to replace the alternatives.

**Not a better agent. A scientifically governed system for discovering better ways to solve problems.**

See [GOAL.md](GOAL.md) for the full destination statement.

---

The coding model is not the authority. The repository, specifications, invariants, tests, policies, and acceptance rules are the authority. The harness exists to enforce that boundary and to search the space of workflows under explicit constraints.

## The Four Pillars + North Star

| Layer | Fundamental question |
|-------|----------------------|
| **[GOAL.md](GOAL.md)** | What is the cheapest sufficient, verifiably correct workflow? |
| **Authoritative** | What must be true? |
| **Verifier** | How do we know it is true? |
| **Economics** | What is the least costly sufficient way to establish and sustain it? |
| **Observability** | How is the system performing over time, and what should we adapt? |

## Authority Documents

| Document | Purpose |
|----------|---------|
| [GOAL.md](GOAL.md) | Ultimate destination — workflow optimization under evidence |
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

- **Workflow optimization engine**: searches the space of candidate workflows under mandatory floors
- **Authoritative governance**: resolve → constrain → execute → verify → decide
- **Independent declaration of success**: the model never declares completion
- **Hybrid verification**: algorithmic + bounded agentic under explicit contracts
- **Three verification loops**: Agentic, CI, Maintenance
- **Minimum Sufficient Harness**: every control earns its place; cheapest sufficient path at runtime
- **Observability-driven adaptation**: evidence makes control admission and removal empirical
- **Models as replaceable resources**: competitive allocation of intelligence
- **Evidence-backed claims**: optimality / dominance / Pareto efficiency within a defined search space

## The Five Questions the Harness Must Answer

1. What is actually required?
2. What is the agent allowed to change?
3. Did the implementation preserve the system’s invariants?
4. Did the requested outcome actually occur?
5. Who gets to declare success?

## Quick Start (Conceptual)

```bash
pip install -e .

specialized-harness run \
  --blueprint standard-coding \
  --repo /path/to/monorepo \
  --task "Fix the flaky test in payments/invoice_test.rb" \
  --model <provider/model>
```

## License

Apache-2.0
