# Eval #8 — Live OpenAI path on `samples/repo_stats`

**Date**: 2026-08-12  
**Authority**: AGENTS.md · GOAL.md · STATUS.md · OBSERVABILITY.md · VERIFICATION_VS_EVAL.md  
**Run id**: `046e1ec8-2c20-49b1-888e-4dd7a645255e`  
**Artifact**: [`docs/evals/EVAL_008_run.json`](EVAL_008_run.json) (immutable tracked copy; `artifacts/` remains gitignored)

## Design

| Axis | Value |
|------|--------|
| Model / propose source | `HttpAgentProvider` → `http://127.0.0.1:8765` (`scripts/live_propose_server.py`) |
| Mode | **OpenAI** — `OPENAI_API_KEY` set; server `mode=openai` |
| Model id | `gpt-4.1-mini` (via `LIVE_PROPOSE_MODEL`) |
| Repo | `samples/repo_stats` (`--repo`) |
| Task brief | Fix even-length `median` in `statskit/core.py` without regressing mean / odd path |
| Profile / language | `code-change` / `python` |
| Blueprint | `blueprints/standard-coding.yaml` |

Closes the **real-model** live-path bar for the package-tree sample (EVAL_007 offline + rehearsal; this eval live OpenAI). Complements EVAL_002 / EVAL_005 (flat arithmetic samples).

## Outcome

| Field | Value |
|-------|--------|
| **final_status** | **ACCEPT** |
| total_ms | 16716 |
| trajectory_len | 9 |
| trajectory | resolve_authority → constrain_scope → provision → plan → implement → local_verify → push → ci_round → decide |
| Claims | `loc_within_budget` PASS (`net_loc=32`); `syntax_clean` PASS (4 files); `tests_pass` PASS (3 passed) |
| CI rounds | 1 (no `fix_ci`) |
| Provider | HttpAgentProvider (live OpenAI) |
| Source isolation | Mutation only in disposable workspace; sample tree on disk remains broken by design |

## Token profile (OckBench-aligned reporting)

Tokens inform **Cost per Verified Correct Outcome**; they do **not** gate ACCEPT.

| Field | Value |
|-------|--------|
| prompt / completion / total | Not present in operator CLI summary; left empty in tracked artifact rather than invented |
| total_ms | 16716 (from CLI) |

## Scope honesty

- `net_loc=32` is **not** a minimal-edit proof (same honesty as EVAL_006 / EVAL_007): no exact-diff gate; ACCEPT means mandatory ledger claims passed.
- Prior `resolve_authority` FAILED (`92846b32-…`) was local path/pull lag, not an eval outcome; discarded.
- Package tree + partial-green suite exercised under live model.

## Authority check

- Provider returned **mutations only** — model did not declare success.
- Declaration of success: harness ledger + workspace pytest only (Verification harness).
- Trajectory complete (AGENTS.md supporting invariant 9).
- Tracked run artifact present at `docs/evals/EVAL_008_run.json`.

## How to reproduce

```bash
export OPENAI_API_KEY="..."   # valid key; never commit
export LIVE_PROPOSE_MODEL="gpt-4.1-mini"
py -3 scripts/live_propose_server.py   # mode=openai

py -3 -m specialized_harness.cli run \
  --provider http --provider-url http://127.0.0.1:8765 \
  --repo samples/repo_stats \
  --task "Fix the broken median function in statskit/core.py: for even-length inputs return the average of the two middle values (e.g. median([4,1,3,2]) == 2.5). Do not change mean or the odd-length path. Do not touch tests or conftest." \
  --profile code-change --language python \
  --runs-dir artifacts/runs --json
```
