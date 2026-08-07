# Sprint 5 Review

**Date**: 2026-08-07  
**Authority**: AGENTS.md v1.1.0 · OBSERVABILITY.md · ECONOMICS.md  
**Repo**: https://github.com/Lvvphole/specialized-harness  
**Baseline**: Sprint 4 closed (51 tests); latency metrics; modular handlers; accurate README

## Goal

Give offline empirical inputs for harness performance (metrics over persisted runs) and connect an optional live proposal source behind `AgentProvider` without changing acceptance authority.

## Exit criteria

| ID | Item | Evidence |
|----|------|----------|
| S5-1 | Offline run metrics | `summarize_runs_dir`; CLI `metrics --runs-dir`; accept/handoff rates, mean_total_ms, claim counts |
| S5-2 | HTTP `AgentProvider` boundary | `HttpAgentProvider` + `provider_from_env`; Scripted default; mocked tests; ACCEPT still ledger+CI |
| S5-3 | README → Sprint 4 review | Done at Sprint 4 close |

## Definition of Done checklist

- [x] Offline metrics do not alter ACCEPT/HANDOFF logic
- [x] Live provider is env-gated; default remains ScriptedProvider
- [x] No ACCEPT from model/HTTP text alone
- [x] No CI dependency on live API keys
- [x] pytest: **59 passed** on GitHub `main`

## LOC budget

| Scope | Lines (approx) |
|-------|----------------|
| `src/` production | ~1586 |
| `tests/` | ~854 |
| Per-slice work | Each under 1000 LOC |

## Retrospective

### What worked

- Metrics are pure read-path aggregation over `run.json` — Minimum Sufficient observability without decide coupling.
- HTTP provider protocol + injectable opener kept CI offline while proving ACCEPT still requires product tests.
- `provider_from_env` is a single gate; operators opt into live providers deliberately.

### What hurt

- Cumulative LOC (~1.6k src) continues to climb; Sprint 6 should favor prune-or-earn over new surface.
- HTTP contract is minimal (`node_id`/`task`/`run_id` → mutations); richer context (diff, failing tests) is not yet standardized.
- Cost-per-verified-correct-outcome still lacks token accounting (only latency).

### Decisions

1. Keep ScriptedProvider as the documented default for demos and CI.
2. Expand HTTP request context only when a real provider integration needs it (not preemptively).
3. Sprint 6: prefer hardening (token fields, context payload, maintenance spike) over new control planes.

### Backlog adaptation

- Sprint 5 items **closed**.
- Next themes: richer provider context; optional token_usage population; maintenance-loop spike; LOC prune pass.
