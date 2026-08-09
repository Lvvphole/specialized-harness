# Eval #2 — Live OpenAI path on `samples/repo_add`

**Date**: 2026-08-09  
**Authority**: AGENTS.md · GOAL.md · STATUS.md §4 · OBSERVABILITY.md  
**Run id**: `af60d7e1-8ca1-4d22-a2ac-cff01607eac3`  
**Artifact**: [`docs/evals/EVAL_002_run.json`](EVAL_002_run.json) (immutable tracked copy of the full persisted run; `artifacts/` remains gitignored)

## Design

| Axis | Value |
|------|--------|
| Model / propose source | `HttpAgentProvider` → `http://127.0.0.1:8765` (`scripts/live_propose_server.py`) |
| Mode | **OpenAI** — `OPENAI_API_KEY` set; server mode=`openai` |
| Model id | `gpt-4.1-mini` (default `LIVE_PROPOSE_MODEL`) |
| Repo | `samples/repo_add` (`--repo`) |
| Task brief | `Fix the broken add function` |
| Profile / language | `code-change` / `python` (Agent Engineering Standard guidance attached) |
| Blueprint | `blueprints/standard-coding.yaml` |

## Outcome

| Field | Value |
|-------|--------|
| **final_status** | **ACCEPT** |
| total_ms | 23 987 |
| trajectory_len | 12 |
| trajectory | resolve_authority → constrain_scope → provision → plan → implement → local_verify → push → ci_round → fix_ci → push → ci_round → decide |
| Claims | `loc_within_budget` PASS (net_loc=3); `syntax_clean` PASS; `tests_pass` FAIL then PASS |
| CI behavior | Round 1 pytest FAIL (`assert -1 == 5`); `fix_ci` then round 2 PASS — within hard max of 2 CI rounds |
| implement tools | `search_code`, `read_file(app.py)`; http_rounds=3 |
| fix_ci tools | `search_code`, `read_file(add.py)`; files_changed includes `app.py` |
| Source isolation | Disposable workspace under `%TEMP%\harness-af60d7e1-*`; sample tree on disk unchanged by design |

## Token usage (from trajectory)

| Node | prompt | completion |
|------|--------|------------|
| plan | 2206 | 105 |
| implement | 2189 | 121 |
| fix_ci | 2127 | 175 |
| **sum (agentic)** | **6522** | **401** |

## Authority check

- Provider returned **mutations only** — no ACCEPT claim from the model path.
- Declaration of success: harness ledger + workspace pytest only (`decide` requires `last_ci_ok`).
- Agent standard attached as candidate guidance only.
- Two CI rounds used; control surrendered after the second green round → ACCEPT.
- Trajectory complete: every node has `sequence`, `duration_ms`, `token_usage`, `tools_called`, and `metadata` (AGENTS.md §2 supporting invariant 9).

## Cost / competence note

- Real-model path: ~24 s vs EVAL_001 rehearsal (557 ms).
- Multi-round repair under the hard CI limit: first implement left tests red; `fix_ci` + second `ci_round` produced green evidence.
- Full per-node evidence (tools, tokens, isolation paths) is in the tracked run artifact.

## How to reproduce

```bash
# terminal 1 — requires OPENAI_API_KEY
export OPENAI_API_KEY="sk-..."
# optional
export LIVE_PROPOSE_MODEL="gpt-4.1-mini"
python3 scripts/live_propose_server.py
# expect: mode=openai

# terminal 2
py -3 -m specialized_harness.cli run \
  --provider http --provider-url http://127.0.0.1:8765 \
  --repo samples/repo_add \
  --task "Fix the broken add function" \
  --profile code-change --language python \
  --runs-dir artifacts/runs --json
```

Windows / Git Bash: if `specialized-harness` is not on PATH, use `py -3 -m specialized_harness.cli` as above.

## Verdict for harness development

Eval #2 **passes** the STATUS.md live-path bar with a **real model**:

- HTTP multi-round tool protocol
- Sandbox isolation
- Independent ACCEPT (ledger + pytest)
- Hard CI-round limit observed and sufficient for recovery
- Complete trajectory persisted and tracked

Next: broader task corpus and optional multi-model comparison under the same contract.
