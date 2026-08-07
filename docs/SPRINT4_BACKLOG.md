# Sprint 4 Backlog

**Authority**: AGENTS.md, ECONOMICS.md, OBSERVABILITY.md, GOAL.md  
**Constraint**: ≤ 1000 LOC per sprint slice  
**Sprint 3 baseline**: 48 tests green; product-code ACCEPT; honest git; run persistence

**Progress (2026-08-07):** S4-1 latency/total_ms done · S4-2 registry modularization done · S4-4 README demos done · S4-3 live provider still stretch

## Sprint 4 goal (proposed)

> Make harness cost and latency measurable per run, and optionally introduce a live provider behind the existing `AgentProvider` boundary — without weakening independent acceptance.

## Ordered items

### S4-1 — Per-node latency + run total_ms (P0)

**Story**: Record duration on each trajectory event and `total_ms` on persisted run JSON (ECONOMICS.md scaffolding).

**Acceptance**
- [x] Each trajectory event includes `duration_ms` (or equivalent)
- [x] `run.json` includes `total_ms`
- [x] ACCEPT/HANDOFF behavior unchanged
- [x] Unit + one integration assertion

**Estimate**: ~40–80 LOC

---

### S4-2 — Registry modularization (P1)

**Story**: Split `registry.py` handlers into focused modules (deterministic vs agentic) to reduce blast radius and honor Minimum Sufficient readability.

**Acceptance**
- [x] Public handler map unchanged for blueprint
- [x] All existing tests green
- [x] No behavior change

**Estimate**: ~150–250 LOC moved (net new low)

---

### S4-3 — Live / HTTP provider boundary (P1, optional)

**Story**: `HttpAgentProvider` implementing `AgentProvider`; env-gated; mutations only via `apply_proposal`; tests mocked.

**Acceptance**
- [ ] Protocol satisfied
- [ ] Default remains ScriptedProvider
- [ ] No ACCEPT from model text alone
- [ ] No CI dependency on live API keys

**Estimate**: ~150–250 LOC

---

### S4-4 — Sprint 1–3 authority doc cross-links in README (P2)

**Story**: README table of sprints + how to run ACCEPT/HANDOFF demos.

**Acceptance**
- [x] Real CLI flags documented
- [x] ACCEPT / HANDOFF / over_loc demos
- [x] Sprint history table with doc links

**Estimate**: docs only

---

### Out of scope

| Item | Why |
|------|-----|
| Full maintenance loop | Post-merge lifecycle |
| Multi-model Pareto search | Needs eval corpus |
| Remote git push with credentials | Explicitly deferred; honesty retained |

## Recommended Sprint 4 commitment

| Must | Stretch |
|------|---------|
| S4-1 latency / total_ms | S4-3 live provider |
| S4-2 registry split (if touching handlers) | |
| S4-4 README | |

## Draft exit criteria

1. Persisted runs expose `total_ms` and per-node durations.
2. pytest green; ≤ 1000 LOC for the implementing slice.
3. AGENTS.md five questions still answerable with evidence.
4. README documents real fixture demos and sprint history.
