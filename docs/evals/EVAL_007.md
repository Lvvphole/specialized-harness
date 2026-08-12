# Eval #7 — Third sample (`samples/repo_stats`) offline ACCEPT (corpus growth)

**Date**: 2026-08-12  
**Authority**: AGENTS.md · GOAL.md · STATUS.md §5 · OBSERVABILITY.md  
**Run id**: `0d70b125-f9db-49a4-831d-cd4165713501`  
**Artifact**: [`EVAL_007_run.json`](EVAL_007_run.json) (tracked copy of the persisted run; absolute repo/temp paths redacted, claims and trajectory unmodified; `artifacts/` remains gitignored)

## Design

| Axis | Value |
|------|--------|
| Model / propose source | `ScriptedProvider` (offline deterministic) |
| Mode | Offline corpus growth — third distinct product tree |
| Repo | `samples/repo_stats` (`--repo`) |
| Task brief | `Fix the broken median function` |
| Blueprint | `blueprints/standard-coding.yaml` |

This sample moves the corpus on two axes at once, which is why it was added rather
than a fourth arithmetic variant (ECONOMICS.md — a sample must earn its place):

| Axis | `repo_add` / `repo_mul` | `repo_stats` |
|------|-------------------------|--------------|
| Tree shape | flat `app.py` + `test_app.py` | package `statskit/` + `tests/` + root `conftest.py` |
| Repair target | top-level `app.py` | nested module `statskit/core.py` |
| Bug class | arithmetic operator swap (one token) | even-length boundary case in `median` (branch, multi-line) |
| Starting test state | 1 test, red | 3 tests, 2 green / 1 red — the repair must not regress the green ones |

## Outcome

| Field | Value |
|-------|--------|
| **final_status** | **ACCEPT** |
| total_ms | 381 |
| trajectory_len | 9 |
| trajectory | resolve_authority → constrain_scope → provision → plan → implement → local_verify → push → ci_round → decide |
| Claims | `loc_within_budget` PASS (`net_loc=9`); `syntax_clean` PASS (compiled 4 files); `tests_pass` PASS (3 passed) |
| Files changed | `statskit/core.py`, `harness_impl_marker.txt` |
| Source isolation | Sample tree on disk still returns `ordered[len(ordered) // 2]`; mutation only in the disposable workspace |

## Live HTTP rehearsal (same sample, out-of-process provider)

Run id `808cc77b-b254-41be-82d5-04b115605490` — `HttpAgentProvider` against
`scripts/live_propose_server.py` in **rehearsal** mode (no `OPENAI_API_KEY` in this
environment): **ACCEPT**, `net_loc=8`, 3 passed, total_ms 413. The provider read
`statskit/core.py` and `tests/test_core.py` through the tool protocol before proposing.

This confirms the multi-file sample works through the HTTP provider boundary. It is
**not** a real-model result — no live model was called. Real-model confirmation on
this sample (the EVAL_002 / EVAL_005 contract) remains open.

## Authority check

- Provider returned **mutations only** — no ACCEPT claim from the provider path.
- Declaration of success: harness ledger + workspace pytest only.
- Trajectory complete, 9 nodes (AGENTS.md supporting invariant 9).
- Regression guard: the offline repair is asserted in
  `tests/integration/test_repo_mode_accept.py` and in the eval contracts
  (`tests/evals/test_offline_contracts.py`), including source-tree isolation.

## Scope honesty

Harness **ACCEPT** here means the mandatory ledger claims passed — workspace pytest
green, syntax clean, net LOC inside budget. As in EVAL_006, there is no exact-diff or
minimal-edit gate: the provider replaced `statskit/core.py` wholesale (`net_loc=9`),
which the shipped gates permit. Do not read this eval as evidence of minimal-edit
discipline, and do not read a third sample as general monorepo competence.

## How to reproduce

```bash
specialized-harness run \
  --repo samples/repo_stats \
  --task "Fix the broken median function" \
  --runs-dir artifacts/runs --json

# rehearsal / live path (terminal 1 then terminal 2):
python3 scripts/live_propose_server.py
specialized-harness run --provider http --provider-url http://127.0.0.1:8765 \
  --repo samples/repo_stats --task "Fix the broken median function" \
  --runs-dir artifacts/runs --json
```

## Verdict for harness development

Eval #7 **passes** STATUS.md §5 move 1 (corpus growth beyond two samples) for a third
offline product tree under independent ACCEPT, and extends the corpus past flat
single-file trees and single-token operator bugs for the first time.
