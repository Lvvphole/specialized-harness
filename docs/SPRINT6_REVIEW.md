# Sprint 6 Review

**Date**: 2026-08-07  
**Authority**: AGENTS.md v1.1.0 · ECONOMICS.md · OBSERVABILITY.md · GOAL.md  
**Repo**: https://github.com/Lvvphole/specialized-harness  
**Baseline**: Sprint 5 closed (59 tests); offline metrics; env-gated HttpAgentProvider

## Goal

Harden the provider and economics surfaces already present — richer proposal context, optional token accounting — and explicitly prune dead weight under the Minimum Sufficient Harness Principle.

## Exit criteria

| ID | Item | Evidence |
|----|------|----------|
| S6-1 | Provider request context enrichment | `build_propose_body`; optional `net_loc` / `last_ci_ok` / `last_ci_stdout`; CI stores truncated stdout on evidence |
| S6-2 | `token_usage` on trajectory | `normalize_token_usage`; HTTP → proposal → NodeResult → TrajectoryEvent; metrics `mean_total_tokens` |
| S6-3 | Net-negative LOC prune | Removed unused aliases/helpers; src ~1662 → ~1621 lines |

## Definition of Done checklist

- [x] Optional propose context does not fail when absent
- [x] Token fields are backward compatible; no ACCEPT/HANDOFF change
- [x] Net LOC of production source decreased without test loss
- [x] pytest: **67 passed** on GitHub `main`

## LOC budget

| Scope | Lines (approx) |
|-------|----------------|
| `src/` production | ~1621 |
| `tests/` | ~1049 |
| Per-slice work | Each under 1000 LOC; S6-3 net-negative |

## Retrospective

### What worked

- Context enrichment stayed proposal-only — Minimum Sufficient for live providers without coupling decide.
- Token path reused existing `TrajectoryEvent.token_usage` and metadata plumbing.
- Prune removed real dead surface (`hydrate_context`, `create_pull_request` wrappers, `canonical_hash`, `run_with_handlers`) while keeping engine `selective_ci` alias.

### What hurt

- Cumulative test LOC still grows with each slice; prune focused on `src/`.
- Multi-model routing, Pareto workflow search, and full Code Maintenance Loop remain specified in authority docs but unbuilt — eval corpus still too thin.
- Direct pushes to `main` (no PR) remain operational practice; authority docs do not yet require sole-owner merge gates.

### Decisions

1. Sprint 6 closed with all three backlog items done.
2. Multi-model / Pareto / maintenance stay **deferred** until eval volume justifies control surface (GOAL.md offline loop).
3. Prefer review + thin hardening over new control planes next.

### Backlog adaptation

- Sprint 6 items **closed**.
- Next themes: Sprint 7 thin hardening only if justified; otherwise accumulate eval runs / document Done boundary vs deferred epics.
