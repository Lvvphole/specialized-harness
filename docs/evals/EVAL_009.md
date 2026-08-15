# Eval #9 — Offline meta-verification on `samples/repo_sub`

**Date**: 2026-08-15  
**Authority**: AGENTS.md · GOAL.md · STATUS.md · VERIFICATION_VS_EVAL.md · OBSERVABILITY.md  
**Run id**: `b0f079b1-2ace-4c27-b785-7170be5ac6c3`  
**Artifact**: [`docs/evals/EVAL_009_run.json`](EVAL_009_run.json)

> **Provenance:** This JSON is a **path-redacted copy of a real `persist_run` output** from:
> `specialized-harness.cli run --provider scripted --repo samples/repo_sub --task "Fix the broken subtract function"`.
> No trajectory fields were invented or reconstructed. Absolute paths only were string-redacted.

## Design

| Axis | Value |
|------|--------|
| Model / propose source | `ScriptedProvider` (offline deterministic) |
| Mode | **Meta-verification + unit contract** — no live model |
| Repo | `samples/repo_sub` (`--repo`) |
| Task brief | `Fix the broken subtract function` |
| Blueprint | `blueprints/standard-coding.yaml` |

**Meta-verification** floor:

1. **Unit red on source** — `pytest samples/repo_sub` is **executed** and must fail while broken.
2. **Offline ACCEPT** — ScriptedProvider under independent ledger + workspace pytest.
3. **Source isolation** — source tree unchanged after ACCEPT (before/after content assert).
4. **Checker qualification suite** — Sprint 8 floor still discriminates.

## Outcome (from real run)

| Field | Value |
|-------|--------|
| **final_status** | **ACCEPT** |
| total_ms | **518** (equals sum of event `duration_ms`) |
| trajectory_len | 9 |
| Claims | loc PASS (`net_loc=5`); syntax PASS; tests_pass PASS |
| plan metadata | `plan` + `workspace` (engine field names) |
| ci_round | duration 496 ms; distinct `started_at` / `finished_at`; `tests_passed: true` |
| Source isolation | asserted in offline + integration tests |

## Unit + meta evidence (executed)

| Check | Result |
|-------|--------|
| `pytest samples/repo_sub` | FAIL (required non-zero exit before ACCEPT) |
| `test_eval_accept_repo_mode_sample_sub` | **PASSED** |
| `test_repo_mode_accept_fix_sub_sample` | **PASSED** |
| checker qualification | **3 passed** |

## How to reproduce

```bash
pytest samples/repo_sub -q   # must fail

py -3 -m specialized_harness.cli run \
  --provider scripted \
  --repo samples/repo_sub \
  --task "Fix the broken subtract function" \
  --runs-dir artifacts/runs --json

pytest tests/evals/test_offline_contracts.py::test_eval_accept_repo_mode_sample_sub -q
pytest tests/integration/test_repo_mode_accept.py::test_repo_mode_accept_fix_sub_sample -q
```
