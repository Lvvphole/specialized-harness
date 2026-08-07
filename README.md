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

## Install

```bash
git clone https://github.com/Lvvphole/specialized-harness.git
cd specialized-harness
pip install -e ".[dev]"
pytest -q   # expect green (currently 59 tests)
```

## Quick Start (fixture demos)

The runtime CLI runs the `standard-coding` blueprint against **fixture** tasks. The default provider is `ScriptedProvider` (no live model required). Acceptance is decided only by the ledger + CI evidence, never by the model.

### ACCEPT path (`fix_add`)

Product code starts **broken**; the scripted implementer repairs `app.py` in a disposable workspace; pytest in the workspace must pass.

```bash
specialized-harness run \
  --blueprint blueprints/standard-coding.yaml \
  --fixture-root fixtures \
  --task fix_add \
  --json
```

Expected: `final_status=ACCEPT`. Run artifacts: `artifacts/runs/<run_id>/run.json` (trajectory, claims, `total_ms`).

### HUMAN_HANDOFF path (`always_fail_ci`)

```bash
specialized-harness run \
  --blueprint blueprints/standard-coding.yaml \
  --fixture-root fixtures \
  --task always_fail_ci \
  --json
```

Expected: `final_status=HUMAN_HANDOFF` after two real CI failures (max two CI rounds; no third).

### LOC budget rejection (`over_loc`)

```bash
specialized-harness run \
  --blueprint blueprints/standard-coding.yaml \
  --fixture-root fixtures \
  --task over_loc \
  --json
```

Expected: not `ACCEPT` when measured net LOC exceeds `max_net_loc` (1000).

## Sprint history

| Sprint | Theme | Status | Review / backlog |
|--------|--------|--------|------------------|
| **1** | Control plane (engine, policy, ACCEPT/HANDOFF) | Closed | [SPRINT1_REVIEW.md](docs/SPRINT1_REVIEW.md) |
| **2** | Real sandbox, verify, LOC, ledger, provider | Closed | [SPRINT2_REVIEW.md](docs/SPRINT2_REVIEW.md) |
| **3** | Product-code fix, honest git, persistence | Musts closed | [SPRINT3_REVIEW.md](docs/SPRINT3_REVIEW.md) · [SPRINT3_BACKLOG.md](docs/SPRINT3_BACKLOG.md) |
| **4** | Latency metrics, registry modularization, docs | Closed | [SPRINT4_REVIEW.md](docs/SPRINT4_REVIEW.md) · [SPRINT4_BACKLOG.md](docs/SPRINT4_BACKLOG.md) |
| **5** | Offline metrics + HTTP provider boundary | Closed | [SPRINT5_REVIEW.md](docs/SPRINT5_REVIEW.md) · [SPRINT5_BACKLOG.md](docs/SPRINT5_BACKLOG.md) |

## Repository layout (runtime)

```text
src/specialized_harness/
  engine/           # BlueprintEngine state machine, models
  nodes/            # deterministic + agentic handlers, registry
  providers/        # AgentProvider protocol, ScriptedProvider, HttpAgentProvider
  sandboxes/        # disposable workspace isolation
  observability/    # EvidenceLedger, run persistence, metrics
  policy/           # CI/LOC/trajectory enforcer
blueprints/         # standard-coding.yaml
fixtures/           # fix_add, always_fail_ci, over_loc
docs/               # sprint reviews and backlogs
```

## License

Apache-2.0
