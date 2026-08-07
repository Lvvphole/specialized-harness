# Specialized Agentic Harness

[![CI](https://github.com/Lvvphole/specialized-harness/actions/workflows/ci.yml/badge.svg)](https://github.com/Lvvphole/specialized-harness/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)
[![Version 1.1.0](https://img.shields.io/badge/version-1.1.0-informational)](pyproject.toml)

**A model-agnostic optimization system for discovering, executing, verifying, and economically selecting workflows for complex problem solving.**

> Find the cheapest sufficient workflow that can reliably solve the problem, prove that it works, and prove why it deserves to replace the alternatives.

**Not a better agent. A scientifically governed system for discovering better ways to solve problems.**

The coding model is not the authority. The repository, specifications, invariants, tests, policies, and acceptance rules are the authority. The harness enforces that boundary and searches the space of workflows under explicit constraints. See [GOAL.md](GOAL.md) for the full destination statement and [AGENTS.md](AGENTS.md) for the behavioral contract.

---

## Contents

- [What the harness does](#what-the-harness-does)
- [Install](#install)
- [Quick start](#quick-start)
- [How a run works](#how-a-run-works)
- [Evidence and acceptance](#evidence-and-acceptance)
- [Offline metrics](#offline-metrics)
- [Providers](#providers)
- [Authority documents](#authority-documents)
- [Repository layout](#repository-layout)
- [Development](#development)
- [Sprint history](#sprint-history)
- [Status and non-goals](#status-and-non-goals)
- [License](#license)

---

## What the harness does

Every run performs one required transformation:

```text
probabilistic proposal → constrained execution → objective verification → authoritative acceptance or rejection
```

The harness answers five questions on every run ([AGENTS.md §1](AGENTS.md)):

| # | Question | Enforced by |
|---|----------|-------------|
| 1 | What is actually required? | `resolve_authority` — blocking if authority is missing |
| 2 | What is the agent allowed to change? | `constrain_scope` + disposable workspace sandbox |
| 3 | Were the system's invariants preserved? | `local_verify` (`py_compile`), net-LOC budget |
| 4 | Did the requested outcome actually occur? | `ci_round` — real `pytest` executed in the workspace |
| 5 | Who declares success? | `decide` — reads the evidence ledger, never the model |

### Core properties

- **Workflow optimization engine** — searches candidate workflows under mandatory correctness floors
- **Authoritative governance** — `resolve → constrain → execute → verify → decide`
- **Independent declaration of success** — a provider can propose file mutations and nothing else
- **Hybrid verification** — deterministic checks plus bounded agentic work under explicit contracts
- **Three verification loops** — Agentic, CI, Maintenance ([VERIFICATION.md](VERIFICATION.md))
- **Minimum Sufficient Harness** — every control must earn its place ([ECONOMICS.md](ECONOMICS.md))
- **Full trajectories** — every node emits a structured event; incomplete trajectories are infrastructure failures
- **Models as replaceable resources** — competitive allocation of intelligence, not a fixed vendor

---

## Install

Requires Python 3.11 or newer. Runtime dependencies are `pydantic` and `pyyaml`; `pytest` is the only dev dependency.

```bash
git clone https://github.com/Lvvphole/specialized-harness.git
cd specialized-harness
pip install -e ".[dev]"
pytest -q
```

Expected: `63 passed`. If the `pytest` on your `PATH` resolves to a different interpreter than the one you installed into, run `python -m pytest -q` instead.

---

## Quick start

The CLI runs the `standard-coding` blueprint against **fixture** tasks in `fixtures/`. The default provider is `ScriptedProvider`, so no live model or network access is required. Acceptance is decided only by the evidence ledger and executed CI, never by the provider.

### 1. ACCEPT — `fix_add`

Product code ships **broken**. The provider proposes a repair to `app.py`; the harness applies it inside a disposable workspace; `pytest` must then pass in that workspace.

```bash
specialized-harness run \
  --blueprint blueprints/standard-coding.yaml \
  --fixture-root fixtures \
  --task fix_add \
  --json
```

```json
{
  "final_status": "ACCEPT",
  "trajectory_len": 9,
  "nodes": ["resolve_authority", "constrain_scope", "provision", "plan",
            "implement", "local_verify", "push", "ci_round", "decide"],
  "error": null,
  "total_ms": 329
}
```

### 2. HUMAN_HANDOFF — `always_fail_ci`

The fixture test can never pass. The harness runs CI, attempts one scripted fix, runs CI a second time, then surrenders control. There is no third round.

```bash
specialized-harness run \
  --blueprint blueprints/standard-coding.yaml \
  --fixture-root fixtures \
  --task always_fail_ci \
  --json
```

Result: `final_status = HUMAN_HANDOFF` after two real CI failures — 12 trajectory events, with `push → ci_round → fix_ci → push → ci_round → decide`.

### 3. FAILED — `over_loc`

The provider proposes a 1,200-line file. The LOC budget is enforced at `implement`, before verification is ever reached.

```bash
specialized-harness run \
  --blueprint blueprints/standard-coding.yaml \
  --fixture-root fixtures \
  --task over_loc \
  --json
```

Result: `final_status = FAILED` — the run stops after 5 nodes with a `loc_within_budget: FAIL` claim, because measured net LOC exceeds `max_net_loc` (1000).

Every run writes `artifacts/runs/<run_id>/run.json` containing the full trajectory, the evidence claims, `total_ms`, and per-node `duration_ms`.

---

## How a run works

`blueprints/standard-coding.yaml` declares the nodes, edges, and policy. The engine is a state machine over that graph — the provider cannot add nodes, reorder them, or skip a gate.

```text
resolve_authority → constrain_scope → provision → plan → implement → local_verify → push → ci_round → decide
                                                            ▲              │                  │
                                                            └──────────────┘                  │
                                                     recovery (≤ 1 attempt)                   │
                                                                          fix_ci ← failure ───┘
                                                                             │      (ci_rounds < 2)
                                                                             └──→ push
```

| Node | Type | Behavior |
|------|------|----------|
| `resolve_authority` | deterministic | Resolves the fixture task directory; missing authority blocks the run |
| `constrain_scope` | deterministic | Pins the writable path set to the workspace root |
| `provision` | deterministic | Copies the fixture into a unique temp workspace; fingerprints the source |
| `plan` | agentic | Provider returns a plan summary only — no mutations |
| `implement` | agentic | Provider proposes file mutations; **the harness** applies them, measures net LOC, and enforces the budget |
| `local_verify` | deterministic | `py_compile` over the workspace; emits the `syntax_clean` claim |
| `push` | deterministic | `git init` / branch / commit **inside the workspace only**; remote push is explicitly reported as skipped |
| `ci_round` | deterministic | Executes `pytest` in the workspace; emits the `tests_pass` claim |
| `fix_ci` | agentic | One bounded repair attempt on concrete CI diagnostics |
| `decide` | deterministic | Reads the ledger and policy state; returns ACCEPT, HUMAN_HANDOFF, or FAILED |

### Policy in force

Declared in the blueprint's `spec.policy` and enforced by `PolicyEnforcer`:

| Key | Value | Effect on violation |
|-----|-------|---------------------|
| `max_ci_rounds` | 2 | After the second failing round, control is surrendered → `HUMAN_HANDOFF` |
| `max_agentic_recovery_attempts` | 1 | No further recovery edge is traversable |
| `max_net_loc` | 1000 | `implement` fails immediately → `FAILED` |
| `require_trajectory` | true | An incomplete trajectory is an infrastructure failure |
| `require_authority_resolution` | true | Unresolved authority blocks the run |

### Isolation

Each run executes in a copy-on-provision temp workspace, torn down afterward. The original fixture tree is SHA-256 fingerprinted before the run and re-checked after it; any mutation of the source is recorded as an `isolation violation` on the result. Path resolution rejects any target that escapes the workspace root. See [SECURITY.md](SECURITY.md).

---

## Evidence and acceptance

The model never declares completion. `decide` reads an **evidence ledger** of `claim → subject → method → observation → verdict` records, each produced by an executed deterministic check.

| Claim | Method | Emitted by |
|-------|--------|------------|
| `loc_within_budget` | `measure_net_loc` | `implement` |
| `syntax_clean` | `py_compile` | `local_verify` |
| `tests_pass` | `pytest` | `ci_round` |

Decision rules, in order:

1. A `FAIL` on `loc_within_budget` → `FAILED`.
2. A mandatory `PASS` on `tests_pass` **and** a passing final CI round → `ACCEPT`.
3. A failing final CI round with `ci_rounds >= max_ci_rounds` → `HUMAN_HANDOFF`.
4. Anything else, including absent evidence → `FAILED` ("insufficient evidence").

A provider claiming success contributes nothing to this decision.

---

## Offline metrics

Aggregate persisted runs across the economics and observability surfaces:

```bash
specialized-harness metrics --runs-dir artifacts/runs --json
```

Reports `runs`, `accept` / `human_handoff` / `failed` counts and rates, `mean_total_ms`, and per-claim `PASS` / `FAIL` tallies over every `artifacts/runs/*/run.json`. This is the raw input to Cost per Verified Correct Outcome ([ECONOMICS.md](ECONOMICS.md)) — the corpus is deliberately still small.

---

## Providers

A provider is the swappable source of proposals. It implements one method and may return only file mutations, a plan summary, and metadata:

```python
class AgentProvider(Protocol):
    def propose(self, node_id: str, context: dict[str, Any]) -> AgentProposal: ...
```

| Provider | Selected when | Notes |
|----------|---------------|-------|
| `ScriptedProvider` | default | Deterministic, offline; used by all fixtures and tests |
| `HttpAgentProvider` | `HARNESS_PROVIDER_URL` is set | `POST` JSON `{node_id, task, run_id}` → `{mutations, plan_summary}` |

```bash
export HARNESS_PROVIDER_URL="https://your-endpoint/propose"
export HARNESS_PROVIDER_TIMEOUT=30   # seconds, default 30
```

Transport, timeout, and decode errors are returned as a proposal `error` and fail the node — they are never silently treated as success. Providers do not touch the workspace; the harness applies every mutation itself.

---

## Authority documents

These documents are the source of truth. Runtime code must enforce them, and must refuse to start if a lower document contradicts a higher one.

| Rank | Document | Purpose |
|------|----------|---------|
| 1 | [GOAL.md](GOAL.md) | North star — workflow optimization under evidence |
| 2 | [AGENTS.md](AGENTS.md) | Primary behavioral contract, five questions, core invariants |
| 3 | [CONSTRAINTS.md](CONSTRAINTS.md) | Hard limits and non-negotiable policies |
| 3 | [VERIFICATION.md](VERIFICATION.md) | Repository-aware hybrid verifier (three loops) |
| 3 | [ECONOMICS.md](ECONOMICS.md) | Total cost of correctness, Minimum Sufficient Harness Principle |
| 3 | [OBSERVABILITY.md](OBSERVABILITY.md) | Trajectories, evals, metrics, drift, adaptation |
| 4 | [ARCHITECTURE.md](ARCHITECTURE.md) | System design as authoritative governor |
| 5 | [BLUEPRINTS.md](BLUEPRINTS.md) | Blueprint schema and required workflows |
| — | [SECURITY.md](SECURITY.md) | Isolation, permissions, threat model |
| — | [docs/WRITING_STYLE.md](docs/WRITING_STYLE.md) | Output standards for trajectories, PRs, handoffs |

Rank 3 documents are parallel. Conflicts are resolved by the higher document.

---

## Repository layout

```text
src/specialized_harness/
  cli.py              # `run` and `metrics` subcommands
  runner.py           # composes sandbox + handlers + ledger + provider
  engine/             # BlueprintEngine state machine, loader, runtime models
  nodes/
    deterministic/    # authority, checks, git_ops, loc, decide
    agentic/          # plan / implement / fix_ci, proposal application
    registry.py       # handler composition
  providers/          # AgentProvider protocol, ScriptedProvider, HttpAgentProvider,
                      #   optional proposal-request context
  sandboxes/          # disposable workspace isolation + source fingerprinting
  observability/      # EvidenceLedger, run persistence, offline metrics
  policy/             # CI / LOC / trajectory enforcement
blueprints/           # standard-coding.yaml
configs/              # example monorepo overlay (selective CI, linters, tool scopes)
fixtures/             # fix_add · always_fail_ci · over_loc
tests/                # 14 unit + 12 integration modules
docs/                 # sprint reviews, backlogs, writing style
```

---

## Development

```bash
pytest -q                      # full suite (63 tests)
pytest tests/unit -q           # deterministic units only
pytest tests/integration -q    # real sandbox + real pytest execution
ruff check src tests           # lint, as run in CI
```

CI runs the suite and `ruff check` on every push and pull request to `main` (`.github/workflows/ci.yml`). ruff is pinned in the `dev` extra and its rule set is declared in `[tool.ruff.lint]`, so the gate does not change when a new ruff is released.

Contributions are governed by the authority documents, not by preference. Before proposing a change:

1. Confirm it does not weaken a core invariant in [AGENTS.md](AGENTS.md) or [GOAL.md](GOAL.md).
2. Show that the new control improves correctness, containment, or authority enforcement — complexity that does not is rejected under the Minimum Sufficient Harness Principle.
3. Keep the slice within 1,000 net LOC.
4. Keep the suite green, and state results factually — no claims beyond what the gates verified.

---

## Sprint history

| Sprint | Theme | Status | Review / backlog |
|--------|-------|--------|------------------|
| **1** | Control plane (engine, policy, ACCEPT/HANDOFF) | Closed | [Review](docs/SPRINT1_REVIEW.md) |
| **2** | Real sandbox, verify, LOC, ledger, provider | Closed | [Review](docs/SPRINT2_REVIEW.md) |
| **3** | Product-code fix, honest git, persistence | Musts closed | [Review](docs/SPRINT3_REVIEW.md) · [Backlog](docs/SPRINT3_BACKLOG.md) |
| **4** | Latency metrics, registry modularization, docs | Closed | [Review](docs/SPRINT4_REVIEW.md) · [Backlog](docs/SPRINT4_BACKLOG.md) |
| **5** | Offline metrics + HTTP provider boundary | Closed | [Review](docs/SPRINT5_REVIEW.md) · [Backlog](docs/SPRINT5_BACKLOG.md) |
| **6** | Provider context, token accounting, LOC prune | S6-1 landed | [Backlog](docs/SPRINT6_BACKLOG.md) |

---

## Status and non-goals

Implemented and test-covered today: the blueprint engine, deterministic gates, the disposable workspace, real `pytest` execution as CI evidence, the evidence ledger, run persistence, offline metrics, and the two providers.

Not yet implemented — described in the authority documents as design intent, not as shipped behavior:

- The Code Maintenance Loop (post-merge lifecycle)
- Multi-model routing and empirical Pareto workflow selection — the eval corpus is still thin
- Credentialed remote git and pull-request creation — `push` is local-commit-only and reports the remote as skipped
- Selective, path-based CI — `configs/example-monorepo/ci_policy.yaml` is an overlay example, not a live code path

---

## License

Apache-2.0. See [LICENSE](LICENSE).
