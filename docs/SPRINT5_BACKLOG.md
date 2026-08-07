# Sprint 5 Backlog

**Authority**: AGENTS.md, ECONOMICS.md, OBSERVABILITY.md, GOAL.md  
**Constraint**: ≤ 1000 LOC per sprint slice  
**Sprint 4 baseline**: 51 tests green; latency metrics; modular handlers; accurate README

## Sprint 5 goal (proposed)

> Optionally connect a live model behind `AgentProvider` without changing acceptance authority, **or** aggregate offline metrics from persisted runs so Cost per Verified Correct Outcome has empirical inputs — Minimum Sufficient either way.

## Ordered items

### S5-1 — Offline run metrics summary (P0 candidate)

**Story**: CLI or small module that reads `artifacts/runs/*/run.json` and reports accept rate, handoff rate, mean `total_ms`, claim pass rates.

**Acceptance**
- [ ] Works on a directory of persisted runs
- [ ] Does not change ACCEPT/HANDOFF logic
- [ ] Unit test with fixture JSON

**Estimate**: ~80–120 LOC

---

### S5-2 — Live / HTTP provider boundary (P0/P1, from S4-3)

**Story**: `HttpAgentProvider` implementing `AgentProvider`; env-gated; mutations only via `apply_proposal`; tests mocked.

**Acceptance**
- [ ] Protocol satisfied
- [ ] Default remains ScriptedProvider
- [ ] No ACCEPT from model text alone
- [ ] No CI dependency on live API keys

**Estimate**: ~150–250 LOC

---

### S5-3 — Sprint 4 review links in README (P2)

**Story**: Point Sprint 4 row at `docs/SPRINT4_REVIEW.md` once published.

**Estimate**: docs only

---

### Out of scope

| Item | Why |
|------|-----|
| Full Code Maintenance Loop | Post-merge lifecycle |
| Multi-model Pareto / offline workflow search | Needs larger eval corpus |
| Credentialed remote push | Separate design |

## Recommended Sprint 5 commitment

| Must | Stretch |
|------|---------|
| S5-1 offline metrics **or** S5-2 live provider (pick one primary) | The other |
| S5-3 README link | |

## Draft exit criteria

1. Either live provider is mock-tested and default remains ScriptedProvider, **or** offline metrics tool exists over run JSON.
2. pytest green; ≤ 1000 LOC for the implementing slice.
3. AGENTS.md five questions still answerable with evidence.
