# Eval #5 — Live OpenAI path on second sample (`samples/repo_mul`)

**Date**: 2026-08-11  
**Authority**: AGENTS.md · GOAL.md · STATUS.md · OBSERVABILITY.md · VERIFICATION_VS_EVAL.md  
**Run id**: `1897d3c1-a1f0-47dd-9795-3b588fc08886`  
**Artifact**: [`docs/evals/EVAL_005_run.json`](EVAL_005_run.json) (immutable tracked copy of the full persisted run; `artifacts/` remains gitignored)

## Design

| Axis | Value |
|------|--------|
| Model / propose source | `HttpAgentProvider` → `http://127.0.0.1:8765` (`scripts/live_propose_server.py`) |
| Mode | **OpenAI** — `OPENAI_API_KEY` set; server `mode=openai` |
| Model id | `gpt-4.1-mini` (via `LIVE_PROPOSE_MODEL`) |
| Repo | `samples/repo_mul` (`--repo`) |
| Task brief | `Fix the broken multiply function from a / b to a * b` |
| Profile / language | `code-change` / `python` |
| Blueprint | `blueprints/standard-coding.yaml` |

Closes the **real-model** live-path bar for the second sample (EVAL_003 offline, EVAL_004 rehearsal, this eval live OpenAI). Pair with EVAL_002 (`repo_add` live OpenAI).

## Outcome

| Field | Value |
|-------|--------|
| **final_status** | **ACCEPT** |
| total_ms | 9427 |
| trajectory_len | 9 |
| trajectory | resolve_authority → constrain_scope → provision → plan → implement → local_verify → push → ci_round → decide |
| Claims | `loc_within_budget` PASS (`net_loc=3`); `syntax_clean` PASS; `tests_pass` PASS (1 passed) |
| CI rounds | 1 (no `fix_ci`) |
| Provider | HttpAgentProvider (live OpenAI) |
| Source isolation | Mutation only in disposable workspace; sample tree on disk remains broken by design |

## Token profile (OckBench-aligned reporting)

Tokens inform **Cost per Verified Correct Outcome**; they do **not** gate ACCEPT.

| Field | Value |
|-------|--------|
| prompt / completion / total | Not present in operator CLI summary; per-event `token_usage` left empty in tracked artifact rather than invented |
| total_ms | 9427 (from CLI) |

Operator may replace `EVAL_005_run.json` with a full local `artifacts/runs/.../run.json` (paths redacted) if richer token fields are needed.

## Authority check

- Provider returned **mutations only** — model did not declare success.
- Declaration of success: harness ledger + workspace pytest only (Verification harness).
- Prior 401 on run `3aeea7f3-…` was operator credential failure, not an eval outcome; discarded.
- Trajectory complete (AGENTS.md supporting invariant 9).
- Tracked run artifact present at `docs/evals/EVAL_005_run.json` (Codex P1).

## External calibration (not ACCEPT inputs)

- **OckBench**: joint accuracy × token reporting under matched ACCEPT.
- **Gloaguen et al.**: context cost awareness; this task used a short tool-naming brief, not a long thinking ritual.

## How to reproduce

```bash
export OPENAI_API_KEY="..."   # valid key; never commit
export LIVE_PROPOSE_MODEL="gpt-4.1-mini"
py -3 scripts/live_propose_server.py   # mode=openai

py -3 -m specialized_harness.cli run \
  --provider http --provider-url http://127.0.0.1:8765 \
  --repo samples/repo_mul \
  --task "Fix the broken multiply function from a / b to a * b" \
  --profile code-change --language python \
  --runs-dir artifacts/runs --json
```
