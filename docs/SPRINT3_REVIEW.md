# Sprint 3 Review

**Date**: 2026-08-07  
**Authority**: AGENTS.md v1.1.0  
**Repo**: https://github.com/Lvvphole/specialized-harness  
**Baseline**: Sprint 2 closed (38 tests); control plane + real verify + ledger + provider

## Goal

Close the gap between "governed fixture proof" and "governed coding task on a real change": product-code outcome, honest git side effects, offline run artifacts — still Minimum Sufficient (no live model required).

## Exit criteria — must items

| ID | Item | Evidence |
|----|------|----------|
| S3-1 | Product-code `fix_add` | Fixture starts broken (`a - b`); ScriptedProvider repairs `app.py`; marker-only cannot ACCEPT |
| S3-2 | Honest git/PR | Local init/branch/commit; `remote_push=false`, `remote_push_skipped=true`, `skip_reason=no_remote_configured` |
| S3-3 | Trajectory + ledger persistence | `artifacts/runs/{run_id}/run.json` with trajectory, claims, `final_status` |

## Stretch (not committed)

| ID | Item | Status |
|----|------|--------|
| S3-4 | Live model provider boundary | Deferred |
| S3-5 | Economics latency counters | Deferred to Sprint 4 candidate |

## Definition of Done checklist

- [x] `fix_add` ACCEPT depends on **product** pytest green after real `app.py` mutation
- [x] Source `fix_add` fixture remains broken after runs (isolation)
- [x] No trajectory event claims remote git success without performing it
- [x] Run artifacts persisted and loadable offline
- [x] ACCEPT + HUMAN_HANDOFF still proven end-to-end
- [x] pytest: **48 passed** on GitHub `main`

## LOC budget

| Scope | Lines (approx) |
|-------|----------------|
| `src/` production | ~1338 |
| `tests/` | ~628 |
| Per-slice sprint work | Each slice kept under 1000 LOC |

Cumulative growth continues; ECONOMICS.md Minimum Sufficient review remains open for Sprint 4 (prune vs. earn).

## Evidence commands

```text
specialized-harness run --task fix_add
  → ACCEPT; app.py repaired in workspace; claims tests_pass=PASS
  → artifacts/runs/<run_id>/run.json written

specialized-harness run --task always_fail_ci
  → HUMAN_HANDOFF; push metadata remote_push_skipped=true

specialized-harness run --task over_loc
  → not ACCEPT; loc_within_budget=FAIL
```

## Retrospective

### What worked

- Product-code fixture made Q4 (outcome verification) falsifiable: marker-only provider fails ACCEPT.
- Explicit skip metadata for remote git avoided false authority in trajectory.
- Persistence is a thin JSON write — high observability value for low complexity (Minimum Sufficient).

### What hurt

- Registry remains a large single module; further growth will pressure the 1000 LOC *per sprint* invariant and readability.
- `create_pull_request` is still mostly an alias path; remote PR is correctly skipped but not a first-class node in `standard-coding.yaml`.
- Live model still absent — ScriptedProvider proves governance, not coding competence of a frontier model.

### Decisions

1. Defer S3-4 (HTTP/live provider) until a concrete model + credentials path is required; keep ScriptedProvider default.
2. Carry S3-5 (latency / total_ms) into Sprint 4 as a small ECONOMICS.md scaffold.
3. Prefer registry/handler decomposition if the next sprint adds substantial node logic.

### Backlog adaptation

- Sprint 3 musts **closed**.
- Stretch S3-4, S3-5 → Sprint 4 backlog.
- Next themes: economics telemetry, optional live provider, registry modularization, maintenance loop (later).
