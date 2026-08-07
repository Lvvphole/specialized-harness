# Sprint 7 Backlog (proposed)

**Authority**: AGENTS.md, ECONOMICS.md, OBSERVABILITY.md, GOAL.md  
**Constraint**: ≤ 1000 LOC per sprint slice  
**Sprint 6 baseline**: 67 tests green; provider context; token_usage; net-negative prune

## Sprint 7 goal (proposed)

> Either close the gap between “fixture Done” and operator confidence with the smallest useful hardening, or explicitly mark deferred epics and stop expanding surface until eval evidence demands it.

## Ordered candidates

### S7-1 — Sprint/docs alignment (docs-only, preferred first)

**Story**: README test count + sprint history fully consistent; optional STATUS.md summarizing Done vs deferred (multi-model, Pareto, maintenance).

**Estimate**: docs only (~0 production LOC)

---

### S7-2 — Branch protection / authority note (policy)

**Story**: If desired, add CONSTRAINTS or SECURITY language that `main` requires human PR approval; enforce via GitHub settings (out-of-band).

**Estimate**: docs + ops

---

### S7-3 — Maintenance-loop spike (defer unless demanded)

**Story**: Thin post-run drift signal only if a concrete monorepo need appears.

**Estimate**: 200–400 LOC if started

---

### Explicitly out of scope until eval corpus grows

| Item | Why |
|------|-----|
| Multi-model routing | Thin corpus |
| Pareto workflow selection | Thin corpus |
| Full Code Maintenance Loop | Post-merge lifecycle |

## Recommended commitment

| Must | Stretch |
|------|---------|
| S7-1 docs/Done boundary | S7-2 if owner wants PR-only `main` |

## Draft exit criteria

1. Operators can read Done vs deferred without reading every sprint review.
2. No new control plane without measurable assurance value.
3. pytest green; ≤ 1000 LOC for any code slice.
