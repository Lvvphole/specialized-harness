# CI, unit tests, and evals

**Authority**: AGENTS.md §4, §8 · OBSERVABILITY.md · ECONOMICS.md

Bots and workflows **report status only**. They do **not** merge to `main`.

| Workflow | Role | Gate? |
|----------|------|--------|
| `unit-tests.yml` | `tests/unit` + ruff | Yes |
| `integration-tests.yml` | `tests/integration` | Yes |
| `evals.yml` | Offline DoD contracts (`tests/evals`) + CLI smoke | Yes |
| `ci.yml` | Umbrella of unit + integration + evals | Yes |
| `codex-review.yml` | Advisory PR comment via OpenAI | **No** (skip if no secret) |

## TDD expectation

1. **Red** — failing unit/integration for the behavior.
2. **Green** — minimal implementation.
3. **Eval** — outcome contracts still hold.
4. **Human merge** — after green gates + human review.

## Codex reviewer setup

1. Add repository secret `OPENAI_API_KEY`.
2. Optional env/model override: `CODEX_REVIEW_MODEL` (default `gpt-4.1-mini`).
3. On each PR the bot posts an **advisory** comment. It cannot approve or merge.

## Local

```bash
pytest tests/unit -q
pytest tests/integration -q
pytest tests/evals -m eval -q
```
