# Sprint 3 Backlog

**Authority**: AGENTS.md, VERIFICATION.md, ECONOMICS.md, OBSERVABILITY.md, GOAL.md  
**Constraint**: ≤ 1000 LOC per sprint slice  
**Sprint 2 baseline**: 38 tests green; control plane + real verify + ledger + provider interface

## Sprint 3 goal (proposed)

> Close the gap between "governed fixture proof" and "governed coding task on a real change," by making implement repair product code under ScriptedProvider (or a minimal live provider), and making git/PR nodes honest about side effects — still Minimum Sufficient.

## Ordered items

### S3-1 — Product-code implement for `fix_add` (P0)

**Story**: ScriptedProvider (or task-specific script) repairs `app.py` so the *product* outcome is correct, not only a marker file.

**Acceptance**
- [ ] Broken `fix_add` fixture starts with failing test; after implement, workspace tests pass because product code was fixed
- [ ] ACCEPT still requires ledger `tests_pass=PASS`
- [ ] Marker-only implement is insufficient for ACCEPT on this fixture
- [ ] Source fixture remains unchanged (sandbox isolation)

**Estimate**: ~80–150 LOC

---

### S3-2 — Honest git/PR nodes (P0)

**Story**: `git_push` and `create_pull_request` either perform real local git operations in the workspace or explicitly no-op with trajectory metadata `skipped=true` and reason — never imply success that did not occur.

**Acceptance**
- [ ] Workspace can be initialized as a git repo at provision (optional flag) or push is marked skipped
- [ ] Trajectory records branch name only if branch exists
- [ ] Integration test asserts no false claim of remote push without network/credentials
- [ ] Decide remains independent of git success when CI already proved tests

**Estimate**: ~100–180 LOC

---

### S3-3 — Trajectory + ledger persistence (P1)

**Story**: Write run trajectory JSON + ledger claims to `artifacts/runs/{run_id}/` for offline observability.

**Acceptance**
- [ ] File written after finalize
- [ ] Contains sequence, node_id, exit_status, claims
- [ ] Unit test round-trip load

**Estimate**: ~80–120 LOC

---

### S3-4 — Live model provider stub boundary (P1 / optional)

**Story**: `HttpAgentProvider` (or env-gated) implementing `AgentProvider` that calls an external API; default remains ScriptedProvider. No ACCEPT based on model text.

**Acceptance**
- [ ] Protocol satisfied
- [ ] Network only when explicitly configured
- [ ] Mutations still applied only via `apply_proposal`
- [ ] Tests use mock HTTP; no CI dependency on live keys

**Estimate**: ~150–250 LOC (may be own sprint if large)

---

### S3-5 — Economics counters on trajectory (P2)

**Story**: Record per-node latency_ms and optional token_usage fields already on TrajectoryEvent; emit run-level totals for Cost per Verified Correct Outcome scaffolding.

**Acceptance**
- [ ] Each node event has duration
- [ ] RunResult summary includes total_ms
- [ ] No behavior change to ACCEPT/HANDOFF

**Estimate**: ~40–80 LOC

---

### Explicitly out of scope for Sprint 3

| Item | Why |
|------|-----|
| Full Code Maintenance Loop | Needs post-merge repo lifecycle |
| Multi-model routing / Pareto search | Needs more eval data (GOAL.md offline loop) |
| Container/network isolation | Local tempdir remains Minimum Sufficient |
| Human UI for handoff | CLI + trajectory sufficient |

## Recommended Sprint 3 commitment

| Must | Stretch |
|------|---------|
| S3-1 Product-code fix_add | S3-4 Live provider boundary |
| S3-2 Honest git/PR | S3-5 Economics counters |
| S3-3 Trajectory persistence | |

## Sprint 3 exit criteria (draft)

1. `fix_add` ACCEPT depends on **product** test green after real code mutation.
2. No trajectory event claims remote git success without performing it (or explicit skip).
3. Run artifacts persisted under `artifacts/runs/`.
4. pytest green; ≤ 1000 LOC for the sprint slice.
5. AGENTS.md five questions still answerable with evidence.
