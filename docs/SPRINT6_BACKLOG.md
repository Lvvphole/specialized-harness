# Sprint 6 Backlog

**Authority**: AGENTS.md, ECONOMICS.md, OBSERVABILITY.md, GOAL.md  
**Constraint**: ≤ 1000 LOC per sprint slice  
**Sprint 5 baseline**: 59 tests green; offline metrics; HttpAgentProvider env-gated

## Sprint 6 goal (proposed)

> Harden the provider and economics surfaces already present — richer proposal context, optional token accounting — or explicitly prune dead weight under the Minimum Sufficient Harness Principle.

## Ordered items

### S6-1 — Provider request context enrichment (P0 candidate)

**Story**: HTTP/scripted propose payload may include failing test stdout snippet and net_loc from evidence when present (still proposal-only).

**Acceptance**
- [ ] Optional fields only; missing context does not fail the run
- [ ] ScriptedProvider ignores extras; HttpAgentProvider forwards them
- [ ] Tests cover payload shape with mock opener

**Estimate**: ~60–100 LOC

---

### S6-2 — token_usage on trajectory when provider supplies it (P1)

**Story**: If proposal metadata includes token counts, copy into TrajectoryEvent.token_usage; metrics summary can report mean tokens when present.

**Acceptance**
- [ ] Backward compatible when absent
- [ ] No effect on ACCEPT/HANDOFF

**Estimate**: ~40–80 LOC

---

### S6-3 — LOC / complexity prune pass (P1)

**Story**: Audit largest modules; remove dead aliases or duplicate helpers if any; document size in review.

**Estimate**: variable (prefer net-negative LOC)

---

### Out of scope

| Item | Why |
|------|-----|
| Full maintenance loop | Post-merge lifecycle |
| Multi-model routing / Pareto | Eval corpus still thin |
| Credentialed remote git | Separate design |

## Recommended commitment

| Must | Stretch |
|------|---------|
| S6-1 **or** S6-2 (pick one primary) | The other |
| S6-3 if touching same files | |

## Draft exit criteria

1. Provider or economics surface is measurably richer **or** net LOC decreases without test loss.
2. pytest green; ≤ 1000 LOC for the implementing slice.
3. AGENTS.md five questions still answerable with evidence.
