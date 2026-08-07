# Sprint 4 Review

**Date**: 2026-08-07  
**Authority**: AGENTS.md v1.1.0 · ECONOMICS.md · OBSERVABILITY.md  
**Repo**: https://github.com/Lvvphole/specialized-harness  
**Baseline**: Sprint 3 musts closed (48 tests); product-code ACCEPT; honest git; run persistence

## Goal

Make harness cost/latency measurable per run, reduce handler blast radius via modularization, and document real fixture demos — without weakening independent acceptance or requiring a live model.

## Exit criteria — committed musts

| ID | Item | Evidence |
|----|------|----------|
| S4-1 | Per-node `duration_ms` + run `total_ms` | Trajectory events timed via `perf_counter`; `run.json` includes both; ACCEPT/HANDOFF unchanged |
| S4-2 | Registry modularization | `results.py`, `deterministic/handlers.py`, `agentic/handlers.py`, thin `registry.py`; public map keys stable |
| S4-4 | README demos + sprint history | Real CLI flags; ACCEPT / HANDOFF / over_loc; links to sprint docs |

## Stretch

| ID | Item | Status |
|----|------|--------|
| S4-3 | Live / HTTP `AgentProvider` boundary | Deferred — ScriptedProvider remains default (Minimum Sufficient) |

## Definition of Done checklist

- [x] Persisted runs expose `total_ms` and per-node `duration_ms`
- [x] Handler modules split; all prior paths still green
- [x] README documents install + three fixture demos
- [x] ACCEPT + HUMAN_HANDOFF still proven end-to-end
- [x] pytest: **51 passed** on GitHub `main`

## LOC budget

| Scope | Lines (approx) |
|-------|----------------|
| `src/` production | ~1394 |
| `tests/` | ~688 |
| Per-slice work | Each under 1000 LOC |

## Retrospective

### What worked

- Latency metrics are pure observation: no decide-path coupling (ECONOMICS scaffolding without cost-of-correctness distortion).
- Registry split was a move, not a rewrite — tests proved behavior identity.
- README now matches the real CLI; removed fictional `--repo` / `--model` quick-start.

### What hurt

- Cumulative production LOC continues to grow; Minimum Sufficient reviews should prefer prune-or-earn for Sprint 5+.
- Live provider still absent — governance is proven; coding competence of a frontier model is not.

### Decisions

1. Keep ScriptedProvider as default until a concrete provider + credentials path is required.
2. Do not expand remote git/PR until honesty story and credentials model are designed together.
3. Sprint 5 candidates prioritize either (a) live provider behind the existing protocol, or (b) eval/observability aggregation over persisted runs — not both in one slice if LOC risk is high.

### Backlog adaptation

- Sprint 4 musts **closed**.
- S4-3 → Sprint 5 backlog (optional).
- Next themes: live provider boundary; offline metrics over `artifacts/runs/`; optional maintenance-loop spike.
