# Eval #3 — Second sample (`samples/repo_mul`) offline ACCEPT (corpus expansion)

**Date**: 2026-08-09  
**Authority**: AGENTS.md · GOAL.md · STATUS.md §4 · OBSERVABILITY.md  
**Run id**: `e6c82274-fe77-4999-96b1-6bf78ab57c4e`  
**Artifact**: [`docs/evals/EVAL_003_run.json`](EVAL_003_run.json) (immutable tracked copy of the full persisted run; `artifacts/` remains gitignored)

## Design

| Axis | Value |
|------|--------|
| Model / propose source | `ScriptedProvider` (offline deterministic) |
| Mode | Offline corpus expansion — second distinct product tree |
| Repo | `samples/repo_mul` (`--repo`) |
| Task brief | `Fix the broken multiply function` |
| Profile / language | (default) / python |
| Blueprint | `blueprints/standard-coding.yaml` |

Bug class is distinct from `repo_add` (arithmetic operator / multiply vs add). Same independent-ACCEPT contract.

## Outcome

| Field | Value |
|-------|--------|
| **final_status** | **ACCEPT** |
| total_ms | 325 |
| trajectory_len | 9 |
| trajectory | resolve_authority → constrain_scope → provision → plan → implement → local_verify → push → ci_round → decide |
| Claims | `loc_within_budget` PASS; `syntax_clean` PASS; `tests_pass` PASS |
| Source isolation | Sample tree on disk remains broken (`a / b`); mutation only in disposable workspace |

## Authority check

- Provider returned **mutations only** — no ACCEPT claim from the provider path.
- Declaration of success: harness ledger + workspace pytest only.
- Distinct sample from EVAL_001/002 expands the offline corpus under the same five questions and independent declaration of success.

## How to reproduce

```bash
specialized-harness run \
  --repo samples/repo_mul \
  --task "Fix the broken multiply function" \
  --runs-dir artifacts/runs --json
```

Live HTTP / model path uses the same flags as EVAL_001/002 (with `--provider http` + propose server). Rehearsal server updated to recognise the multiply task.

## Verdict for harness development

Eval #3 **passes** the STATUS.md broader-corpus move for a second offline product tree under independent ACCEPT.  
Live-model confirmation on this sample is the natural follow-on (same contract as EVAL_002).
