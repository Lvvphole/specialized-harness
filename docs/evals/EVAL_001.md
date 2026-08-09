# Eval #1 — Live HTTP path on `samples/repo_add`

**Date**: 2026-08-09  
**Authority**: AGENTS.md · GOAL.md · STATUS.md §4 · OBSERVABILITY.md  
**Run id**: `a032ba27-838d-4a9f-ae7d-a12db2bc32b8`  
**Artifact**: [`docs/evals/EVAL_001_run.json`](EVAL_001_run.json) (immutable tracked copy; `artifacts/` remains gitignored)

## Design

| Axis | Value |
|------|--------|
| Model / propose source | `HttpAgentProvider` → `http://127.0.0.1:8765` (`scripts/live_propose_server.py`) |
| Mode | **Rehearsal** — no `OPENAI_API_KEY` in environment; server used multi-round tools then proposed a fix. Not a third-party frontier model. |
| Repo | `samples/repo_add` (`--repo`) |
| Task brief | `Fix the broken add function` |
| Profile / language | `code-change` / `python` (Agent Engineering Standard guidance attached) |
| Blueprint | `blueprints/standard-coding.yaml` |

## Outcome

| Field | Value |
|-------|--------|
| **final_status** | **ACCEPT** |
| total_ms | 557 |
| trajectory | resolve_authority → constrain_scope → provision → plan → implement → local_verify → push → ci_round → decide |
| Claims | `loc_within_budget` PASS (net_loc=4); `syntax_clean` PASS; `tests_pass` PASS (1 pytest) |
| implement HTTP | 2 rounds; tools `read_file(app.py)`, `read_file(test_app.py)`; then mutation `app.py` |
| Source isolation | `samples/repo_add/app.py` remains broken on disk (workspace-only mutation) |

## Authority check

- Provider returned **mutations only** — no ACCEPT claim from the model path.
- Declaration of success: harness ledger + workspace pytest only.
- Agent standard was attached as candidate guidance only.

## Cost / competence note

- Rehearsal path: essentially zero model cost; validates HTTP multi-round tool protocol + independent acceptance on a real product tree layout.
- **True model eval** requires `OPENAI_API_KEY` (or another propose endpoint) and a re-run under the same contract; then this file should be updated or EVAL_002 opened with model id + token_usage from the provider.

## How to reproduce

```bash
# terminal 1
python3 scripts/live_propose_server.py
# optional: OPENAI_API_KEY=... LIVE_PROPOSE_MODEL=gpt-4.1-mini python3 scripts/live_propose_server.py

# terminal 2
specialized-harness run \
  --provider http --provider-url http://127.0.0.1:8765 \
  --repo samples/repo_add \
  --task "Fix the broken add function" \
  --profile code-change --language python \
  --runs-dir artifacts/runs --json
```

## Verdict for harness development

Eval #1 **passes** the STATUS.md “live path against a real tree” bar for the **HTTP provider + sandbox tools + independent ACCEPT** stack.  
It does **not** yet measure frontier-model competence. Next: same task with a real model key → EVAL_002.
