# Sprint 8 Backlog — Verification vs Eval + Checker qualification

**Authority**: AGENTS.md, VERIFICATION.md, OBSERVABILITY.md, ECONOMICS.md  
**Constraint**: ≤ 1000 LOC per sprint slice  
**Baseline**: main after PR #17 (EVAL_006); offline eval contracts green

## Goal

> Formalize the separation between **verification** (candidate satisfies contract?) and **eval** (component good enough to admit?), and ship a **minimum offline checker-qualification** floor for existing deterministic checkers — without changing ACCEPT authority.

## Musts

### S8-1 — Design contract (docs)

- [x] `docs/VERIFICATION_VS_EVAL.md`
- [x] STATUS pointer + Sprint 8 row
- [x] This backlog

### S8-2 — Offline checker qualification (code)

- [x] `specialized_harness.evals.checker_qualification` — labeled cases, TP/TN/FP/FN
- [x] Qualify `syntax_clean` and `tests_pass` on synthetic workspaces
- [x] `tests/evals/test_checker_qualification.py` (pytest mark `eval`)
- [x] Register `eval` mark in `pyproject.toml`

### S8-3 — Explicit non-goals this sprint

- promptfoo integration (defer until a non-deterministic checker is proposed)
- New checkers on the ACCEPT hot path
- FAR/FRR product metrics dashboard
- Changing `decide` / ledger mandatory claims

## Exit criteria

1. Vocabulary is readable without reading every sprint review.
2. Offline tests prove `syntax_check` and `run_pytest` discriminate valid vs invalid.
3. ACCEPT path unchanged; pytest green; slice ≤ 1000 LOC.
4. Human merge only (AGENTS.md §8).
