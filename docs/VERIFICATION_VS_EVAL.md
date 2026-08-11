# Verification harness vs Eval harness vs Checker qualification

**Authority**: AGENTS.md · VERIFICATION.md · OBSERVABILITY.md · ECONOMICS.md · GOAL.md  
**Status**: Design contract (Sprint 8)  
**Does not change**: Independent ACCEPT (ledger + workspace checks)

---

## Three questions

| Layer | Question | When it runs |
|-------|----------|--------------|
| **Verification harness** | Does **this candidate** satisfy the contract? | Online, every coding run |
| **Eval harness** | Is **this component** good enough to admit? | Offline / corpus / metrics |
| **Checker qualification** | Can **this checker** reliably separate valid from invalid? | Offline, before a checker gates ACCEPT |

```text
Eval harness  →  admits checkers / workflows / models
                     ↓ (only if qualified)
Verification harness  →  runs those checkers on a candidate
                     ↓
                ACCEPT / HANDOFF / FAILED
```

Eval never declares a coding task done.  
Verification never admits a new checker from a single lucky green run.

---

## Mapping to this repository

| Layer | Implementation today |
|-------|----------------------|
| Verification | BlueprintEngine + EvidenceLedger + `syntax_check` / `run_pytest` / net LOC → `decide` |
| Eval | `docs/evals/EVAL_*`, `tests/evals/`, `specialized-harness metrics`, STATUS admit rules |
| Checker qualification | Sprint 8: offline labeled cases → TP/TN/FP/FN for shipped checkers (`tests_pass`, `syntax_clean`) |

## External tools

- **promptfoo** ([Lvvphole/promptfoo](https://github.com/Lvvphole/promptfoo)): candidate **eval** runner for non-deterministic judges/prompts. **Not** on the ACCEPT path.
- Deterministic checkers (`pytest` exit code, `py_compile`) are qualified with plain pytest + labeled workspaces — cheaper and sufficient (Minimum Sufficient; Gloaguen/OckBench: do not multiply cost without payback).

## Admission rule

A checker may gate ACCEPT only if:

1. Offline qualification shows discrimination on labeled valid/invalid cases, and  
2. Marginal Cost per Verified Correct Outcome improves (or a mandatory constraint requires it).

Tokens and eval cost inform Economics; they never redefine truth.
