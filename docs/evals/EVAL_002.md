# Eval #2 — Live OpenAI path on `samples/repo_add`

**Date**: 2026-08-09  
**Authority**: AGENTS.md · GOAL.md · STATUS.md §4 · OBSERVABILITY.md  
**Run id**: `af60d7e1-8ca1-4d22-a2ac-cff01607eac3`  
**Artifact**: [`docs/evals/EVAL_002_run.json`](EVAL_002_run.json) (immutable tracked copy; `artifacts/` remains gitignored)

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
| Claims | `loc_within_budget` PASS (net_loc=3); `syntax_clean` PASS; `tests_pass` FAIL then PASS (2 CI rounds) |
| CI behavior | First pytest failed (`assert -1 == 5`); second round green (1 passed) — within hard max of 2 CI rounds |
| Source isolation | Workspace-only mutation; sample tree on disk unchanged by design |

## Authority check

- Provider returned **mutations only** — no ACCEPT claim from the model path.
- Declaration of success: harness ledger + workspace pytest only.
- Agent standard attached as candidate guidance only.
- Two CI rounds used; control surrendered correctly after the second green round → `decide` → ACCEPT.

## Cost / competence note

- Real-model path: non-zero latency (~24 s) vs EVAL_001 rehearsal (557 ms).
- Demonstrates multi-round repair under the hard CI limit: first implement proposal left tests red; `fix_ci` + second `ci_round` produced green evidence.
- `token_usage` (if emitted by the provider) is recorded in the full trajectory inside the run artifact; CLI summary did not surface aggregate tokens.

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

Windows / Git Bash note: if `specialized-harness` is not on PATH, use `py -3 -m specialized_harness.cli` as above.

## Verdict for harness development

Eval #2 **passes** the STATUS.md live-path bar with a **real model**:

- HTTP multi-round tool protocol
- Sandbox isolation
- Independent ACCEPT (ledger + pytest)
- Hard CI-round limit observed and sufficient for recovery

Next: broader task corpus, token accounting visibility in CLI summary, and optional multi-model comparison under the same contract.
