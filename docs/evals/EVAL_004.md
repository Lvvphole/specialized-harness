# Eval #4 — Live HTTP rehearsal path on second sample (`samples/repo_mul`)

**Date**: 2026-08-09  
**Authority**: AGENTS.md · GOAL.md · STATUS.md §4 · OBSERVABILITY.md  
**Run id**: `1baec317-bc15-4796-95cb-9105d315943c`  
**Artifact**: [`docs/evals/EVAL_004_run.json`](EVAL_004_run.json) (immutable tracked copy of the full persisted run; `artifacts/` remains gitignored)

## Design

| Axis | Value |
|------|--------|
| Model / propose source | `HttpAgentProvider` → `http://127.0.0.1:8765` (`scripts/live_propose_server.py`) |
| Mode | **Rehearsal** — no `OPENAI_API_KEY`; server multi-round tools then proposed multiply fix |
| Repo | `samples/repo_mul` (`--repo`) |
| Task brief | `Fix the broken multiply function` |
| Profile / language | `code-change` / `python` |
| Blueprint | `blueprints/standard-coding.yaml` |

Closes the live-path bar for the second sample under the same independent-ACCEPT contract as EVAL_001 (rehearsal) / EVAL_003 (offline).

## Outcome

| Field | Value |
|-------|--------|
| **final_status** | **ACCEPT** |
| total_ms | 560 |
| trajectory_len | 9 |
| trajectory | resolve_authority → constrain_scope → provision → plan → implement → local_verify → push → ci_round → decide |
| Claims | `loc_within_budget` PASS (net_loc=4); `syntax_clean` PASS; `tests_pass` PASS |
| Provider | HttpAgentProvider (rehearsal) |
| Source isolation | Sample tree on disk remains broken (`a / b`); mutation only in disposable workspace |

## Authority check

- Provider returned **mutations only** — no ACCEPT claim from the model/rehearsal path.
- Declaration of success: harness ledger + workspace pytest only.
- Rehearsal server correctly selected multiply mutation from task (Codex P2 from EVAL_003 closed).
- Trajectory complete (AGENTS.md supporting invariant 9).

## How to reproduce

```bash
# terminal 1
python3 scripts/live_propose_server.py
# expect: mode=rehearsal

# terminal 2
specialized-harness run \
  --provider http --provider-url http://127.0.0.1:8765 \
  --repo samples/repo_mul \
  --task "Fix the broken multiply function" \
  --profile code-change --language python \
  --runs-dir artifacts/runs --json
```

True model eval on this sample requires `OPENAI_API_KEY` (same contract as EVAL_002).

## Verdict for harness development

Eval #4 **passes** the STATUS.md live-path bar for the second sample under rehearsal HTTP.  
Corpus now has offline + live-rehearsal coverage on two distinct product trees. Real-model confirmation on `repo_mul` remains the natural follow-on.
