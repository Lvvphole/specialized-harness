# Eval #9 — Offline meta-verification on `samples/repo_sub`

**Date**: 2026-08-15  
**Authority**: AGENTS.md · GOAL.md · STATUS.md · VERIFICATION_VS_EVAL.md · OBSERVABILITY.md  
**Run id**: `892221b5-322f-487b-bd3a-fa3c09ace3b8`  
**Artifact**: [`docs/evals/EVAL_009_run.json`](EVAL_009_run.json) (faithful `persist_run` payload; absolute paths redacted only; `artifacts/` remains gitignored)

## Design

| Axis | Value |
|------|--------|
| Model / propose source | `ScriptedProvider` (offline deterministic) |
| Mode | **Meta-verification + unit contract** — no live model |
| Repo | `samples/repo_sub` (`--repo`) |
| Task brief | `Fix the broken subtract function` |
| Blueprint | `blueprints/standard-coding.yaml` |

**Meta-verification** here means the Eval-harness floor for this sample (not live-model capability):

1. **Unit red on source** — `pytest samples/repo_sub` is **executed** and must fail while the tree is broken (tests are the authority).
2. **Offline ACCEPT** — ScriptedProvider repair under independent ledger + workspace pytest.
3. **Source isolation** — sample on disk remains broken after ACCEPT (before/after content assert).
4. **Checker qualification suite** — deterministic checkers still discriminate (Sprint 8 floor).

## Outcome

| Field | Value |
|-------|--------|
| **final_status** | **ACCEPT** |
| total_ms | 569 |
| trajectory_len | 9 |
| trajectory | resolve_authority → constrain_scope → provision → plan → implement → local_verify → push → ci_round → decide |
| Claims | `loc_within_budget` PASS (`net_loc=5`); `syntax_clean` PASS; `tests_pass` PASS (1 passed; includes reversed/negative cases) |
| Provider | ScriptedProvider |
| Source isolation | `samples/repo_sub/app.py` still returns `a + b` (before/after content assert) |

## Unit + meta evidence

| Check | Result |
|-------|--------|
| `pytest samples/repo_sub` (broken tree) | **FAILED** (executed in offline + integration contracts) |
| `test_eval_accept_repo_mode_sample_sub` | **PASSED** (unit red + ACCEPT + isolation) |
| Integration `test_repo_mode_accept_fix_sub_sample` | **PASSED** |
| `tests/evals/test_checker_qualification.py` | **3 passed** |
| Offline eval suite (`tests/evals -m eval`) | **9 passed** |

## Authority check

- Provider returned **mutations only** — no ACCEPT claim from the model/scripted path.
- Declaration of success: harness ledger + workspace pytest only (Verification harness).
- Trajectory complete (AGENTS.md supporting invariant 9).
- Tracked run artifact is a **faithful `persist_run` payload**: `artifacts` are lists; plan/implement/push/ci_round/decide metadata retained (including `tool_observations`, `branch`/`local_commit`, `tests_passed`, `last_ci_ok`); only absolute paths redacted.
- `total_ms` equals the sum of trajectory `duration_ms` values.

## Scope honesty

- This is **offline** meta-verification, not a live OpenAI result (that remains open for `repo_sub`).
- Strengthened tests (reversed operand + negative result) remain the contract; constant-`2` / `abs` cannot ACCEPT.

## How to reproduce

```bash
# unit: broken sample must fail
pytest samples/repo_sub -q

# offline ACCEPT
specialized-harness run --provider scripted \
  --repo samples/repo_sub \
  --task "Fix the broken subtract function" \
  --runs-dir artifacts/runs --json

# meta contracts (execute unit red + isolation)
pytest tests/evals -m eval -q
pytest tests/integration/test_repo_mode_accept.py::test_repo_mode_accept_fix_sub_sample -q
pytest tests/evals/test_checker_qualification.py -q
```
