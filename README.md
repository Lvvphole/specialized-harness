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

- [Who it's for](#who-its-for)
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
- [Done boundary](docs/STATUS.md)
- [License](#license)

---

## Who it's for

The harness is for **both**:

- **Engineers / operators** — need repository-conformant changes, enforceable policy, and evidence (trajectory, claims, ACCEPT / HUMAN_HANDOFF / FAILED).
- **Vibe coders** — want deterministic-feeling workflows and clean, verified code with a clear outcome, without treating the model as the source of truth.

Same governed path for both: the model proposes; the harness constrains, verifies, and decides. UX should make that path easy to start and inspect — not replace independent acceptance with a chat transcript. See [AGENTS.md](AGENTS.md) (*Who this serves*).

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

Expected: `118 passed`. If the `pytest` on your `PATH` resolves to a different interpreter than the one you installed into, run `python -m pytest -q` instead.

---

## Quick start

The CLI runs the `standard-coding` blueprint against **fixture** tasks in `fixtures/`. Repo defaults live in `.specialized-harness.yaml`. The default provider is `scripted` (offline). Acceptance is decided only by the evidence ledger and executed CI, never by the provider.

From the repo root:

```bash
specialized-harness run fix_add
```

Example human summary:

```text
ACCEPT  task=fix_add  provider=scripted  9 nodes  376ms
PASS  loc_within_budget · syntax_clean · tests_pass
run   artifacts/runs/<run_id>/run.json
```

Use `--json` for machine-readable output. Override provider with `--provider http --provider-url …` or config/env. See [docs/STATUS.md](docs/STATUS.md) for Done vs deferred.

### 1. ACCEPT — `fix_add`

Product code ships **broken**. The provider proposes a repair to `app.py`; the harness applies it inside a disposable workspace; `pytest` must then pass in that workspace.

```bash
specialized-harness run fix_add
# equivalent explicit form:
specialized-harness run \
  --blueprint blueprints/standard-coding.yaml \
  --fixture-root fixtures \
  --task fix_add
```

### 2. HUMAN_HANDOFF — `always_fail_ci`

```bash
specialized-harness run always_fail_ci
```

Result: `HUMAN_HANDOFF` after two real CI failures.

### 3. FAILED — `over_loc`

```bash
specialized-harness run over_loc
```

Result: `FAILED` when measured net LOC exceeds `max_net_loc` (1000).

Every run writes `artifacts/runs/<run_id>/run.json` with trajectory, claims, and timings.

---

## How a run works

`blueprints/standard-coding.yaml` declares the nodes, edges, and policy. The engine is a state machine over that graph — the provider cannot add nodes, reorder them, or skip a gate.

| Node | Type | Behavior |
|------|------|----------|
| `resolve_authority` | deterministic | Resolves the fixture task directory; missing authority blocks the run |
| `constrain_scope` | deterministic | Pins the writable path set to the workspace root |
| `provision` | deterministic | Copies the fixture into a unique temp workspace; fingerprints the source |
| `plan` | agentic | Provider returns a plan summary only — no mutations |
| `implement` | agentic | Provider proposes file mutations; **the harness** applies them and enforces LOC |
| `local_verify` | deterministic | `py_compile`; emits `syntax_clean` |
| `push` | deterministic | Local git only; remote push reported skipped |
| `ci_round` | deterministic | Workspace `pytest`; emits `tests_pass` |
| `fix_ci` | agentic | One bounded repair attempt |
| `decide` | deterministic | Ledger + policy → ACCEPT / HUMAN_HANDOFF / FAILED |

### Policy in force

| Key | Value | Effect on violation |
|-----|-------|---------------------|
| `max_ci_rounds` | 2 | Second failing round → `HUMAN_HANDOFF` |
| `max_agentic_recovery_attempts` | 1 | No further recovery edge |
| `max_net_loc` | 1000 | `implement` fails → `FAILED` |

---

## Evidence and acceptance

The model never declares completion. `decide` reads the evidence ledger only.

| Claim | Method | Emitted by |
|-------|--------|------------|
| `loc_within_budget` | `measure_net_loc` | `implement` |
| `syntax_clean` | `py_compile` | `local_verify` |
| `tests_pass` | `pytest` | `ci_round` |

---

## Offline metrics

```bash
specialized-harness metrics --runs-dir artifacts/runs --json
```

---

## Providers

| Provider | Selected when | Notes |
|----------|---------------|-------|
| `scripted` | default | Offline fixtures/tests |
| `http` | `--provider http` + URL, or `HARNESS_PROVIDER_URL` | Mutations only; never success text |

---

## Authority documents

| Rank | Document | Purpose |
|------|----------|---------|
| 1 | [GOAL.md](GOAL.md) | North star |
| 2 | [AGENTS.md](AGENTS.md) | Behavioral contract |
| 3 | CONSTRAINTS / VERIFICATION / ECONOMICS / OBSERVABILITY | Parallel pillars |
| — | [docs/STATUS.md](docs/STATUS.md) | **Done vs deferred (canonical)** |

---

## Development

```bash
pytest -q                      # full suite (118 tests)
```

---

## Sprint history

| Sprint | Theme | Status | Review / backlog |
|--------|-------|--------|------------------|
| **1** | Control plane (engine, policy, ACCEPT/HANDOFF) | Closed | [Review](docs/SPRINT1_REVIEW.md) |
| **2** | Real sandbox, verify, LOC, ledger, provider | Closed | [Review](docs/SPRINT2_REVIEW.md) |
| **3** | Product-code fix, honest git, persistence | Musts closed | [Review](docs/SPRINT3_REVIEW.md) |
| **4** | Latency metrics, registry modularization, docs | Closed | [Review](docs/SPRINT4_REVIEW.md) |
| **5** | Offline metrics + HTTP provider boundary | Closed | [Review](docs/SPRINT5_REVIEW.md) |
| **6** | Provider context, token accounting, LOC prune | Closed | [SPRINT6_REVIEW.md](docs/SPRINT6_REVIEW.md) |
| **7** | CLI v1 + Done boundary (STATUS) | S7-1 done | [STATUS.md](docs/STATUS.md) · [SPRINT7_BACKLOG.md](docs/SPRINT7_BACKLOG.md) |

---

## Status and non-goals

**Canonical Done boundary:** [docs/STATUS.md](docs/STATUS.md).

Implemented today: blueprint engine, deterministic gates, sandbox, real pytest CI evidence, ledger, persistence, metrics, token accounting, CLI v1, providers `scripted` and `http`.

Deferred: Code Maintenance Loop; multi-model / Pareto (thin corpus); remote PR; selective CI; monorepo task-contract authority; TUI/editor.

---

## License

Apache-2.0. See [LICENSE](LICENSE).
