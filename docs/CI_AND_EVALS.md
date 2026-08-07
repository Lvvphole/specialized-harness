# CI, unit tests, evals, and Codex review

**Authority**: AGENTS.md §4, §8 · OBSERVABILITY.md · ECONOMICS.md

Bots and workflows **report status only**. They do **not** merge to `main`.

| Workflow | Role | Gate? |
|----------|------|--------|
| `unit-tests.yml` | `tests/unit` + ruff | Yes |
| `integration-tests.yml` | `tests/integration` | Yes |
| `evals.yml` | Offline DoD contracts (`tests/evals`) + CLI smoke | Yes |
| `ci.yml` | Umbrella: unit + integration + evals | Yes |
| `codex-review.yml` | Advisory PR comment via OpenAI | **No** (skips if no secret) |

## TDD expectation

1. **Red** — failing unit/integration for the behavior.
2. **Green** — minimal implementation.
3. **Eval** — outcome contracts still hold (ACCEPT / HANDOFF / FAILED / repo ACCEPT).
4. **Human merge** — after green gates + human review (AGENTS.md §8).

## Codex reviewer setup

1. Add repository secret `OPENAI_API_KEY`.
2. Optional repo variable: `CODEX_REVIEW_MODEL` (default `gpt-4.1-mini`).
3. On each non-draft PR the bot posts an **advisory** comment only.

## Local

```bash
pytest tests/unit -q
pytest tests/integration -q
pytest tests/evals -m eval -q
```
