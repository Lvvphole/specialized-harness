# STATUS.md — Done boundary (what is shipped vs deferred)

**Date**: 2026-08-07  
**Authority**: [AGENTS.md](../AGENTS.md) §4 Definition of Done · [GOAL.md](../GOAL.md)  
**Audience**: Engineers/operators and vibe coders

This file is the short answer to “is the harness done?”  
It is **not** a substitute for the authority documents. Runtime behavior must still match AGENTS.md.

---

## 1. Done for supported tasks

### Fixtures

For `fixtures/fix_add`, `always_fail_ci`, `over_loc`, the harness meets AGENTS.md §4.

### Repo mode (sample)

For `samples/repo_add` with `--repo` + task brief, **ACCEPT** is proven offline (ScriptedProvider + workspace pytest + ledger). Isolation of the sample tree is preserved.

**Proven outcomes**

- **ACCEPT** — fixture product-code repair (`fix_add`)
- **ACCEPT (repo mode)** — `samples/repo_add` via `--repo` + brief
- **HUMAN_HANDOFF** — two CI failures (`always_fail_ci`)
- **FAILED** — net LOC over budget (`over_loc`)

**Suite**: `pytest` **87 passed**.

**Operator UX**

```bash
specialized-harness run fix_add
specialized-harness run --repo samples/repo_add --task "Fix the broken add function"
```

---

## 2. Explicitly deferred

| Item | Why deferred |
|------|----------------|
| Multi-model routing | Eval corpus still thin |
| Pareto / offline workflow search | Eval corpus still thin |
| Full Code Maintenance Loop | Post-merge lifecycle |
| Credentialed remote git + PR creation | Local commit only |
| Selective path-based CI | Example overlay only |
| Full arbitrary monorepo repair | Sample proven; general trees need live provider |
| Claude Code / other SDK providers | Optional; not required for sample Done |
| TUI / editor UI | CLI primary |
| Direct LLM commits to `main` | Forbidden — PRs only (AGENTS.md §8) |

---

## 2b. Repository governance

LLMs/agents open PRs only. **Only a human** (@Lvvphole or designate) merges to `main`.

---

## 3. What Done does *not* mean

- The model is not the authority.
- A chat UI declaring success is not Done.
- Authority text is not shipped behavior.

---

## 4. Next product moves (when justified)

1. Live `HttpAgentProvider` against a real tree with reproducible evals.
2. Selective CI / path policies when a monorepo demands it.
3. Admit controls only when they improve Cost per Verified Correct Outcome.
