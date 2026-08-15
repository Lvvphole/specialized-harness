# Eval #9 — Offline meta-verification on `samples/repo_sub`

**Date**: 2026-08-15  
**Authority**: AGENTS.md · GOAL.md · STATUS.md · VERIFICATION_VS_EVAL.md · OBSERVABILITY.md  
**Run id**: `ecf8bfb4-6f4e-46a3-a7f4-81089395d49a`  
**Artifact**: [`docs/evals/EVAL_009_run.json`](EVAL_009_run.json) (tracked copy; paths redacted; `artifacts/` remains gitignored)

## Design

| Axis | Value |
|------|--------|
| Model / propose source | `ScriptedProvider` (offline deterministic) |
| Mode | **Meta-verification + unit contract** — no live model |
| Repo | `samples/repo_sub` (`--repo`) |
| Task brief | `Fix the broken subtract function` |
| Blueprint | `blueprints/standard-coding.yaml` |

**Meta-verification** here means the Eval-harness floor for this sample (not live-model capability):

1. **Unit red on source** — `pytest samples/repo_sub` fails while the tree is broken (tests are the authority).
2. **Offline ACCEPT** — ScriptedProvider repair under independent ledger + workspace pytest.
3. **Source isolation** — sample on disk remains broken after ACCEPT.
4. **Checker qualification suite** — deterministic checkers still discriminate (Sprint 8 floor).

## Outcome

| Field | Value |
|-------|--------|
| **final_status** | **ACCEPT** |
| total_ms | 433 |
| trajectory_len | 9 |
| trajectory | resolve_authority → constrain_scope → provision → plan → implement → local_verify → push → ci_round → decide |
| Claims | `loc_within_budget` PASS (`net_loc=5`); `syntax_clean` PASS; `tests_pass` PASS (1 passed; includes reversed/negative cases) |
| Provider | ScriptedProvider |
| Source isolation | `samples/repo_sub/app.py` still returns `a + b` |

## Unit + meta evidence

| Check | Result |
|-------|--------|
| `pytest samples/repo_sub` (broken tree) | **FAILED** — `assert 8 == 2` (expected red) |
| `test_eval_accept_repo_mode_sample_sub` | **PASSED** |
| `tests/evals/test_checker_qualification.py` | **3 passed** |
| Offline eval suite (`tests/evals -m eval`) | **9 passed** |

## Authority check

- Provider returned **mutations only** — no ACCEPT claim from the model/scripted path.
- Declaration of success: harness ledger + workspace pytest only (Verification harness).
- Trajectory complete (AGENTS.md supporting invariant 9).
- Tracked run artifact present.

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

# meta contracts
pytest tests/evals -m eval -q
pytest tests/evals/test_checker_qualification.py -q
```
