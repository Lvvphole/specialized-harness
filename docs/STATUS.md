# STATUS.md — Done boundary (what is shipped vs deferred)

**Date**: 2026-08-07  
**Authority**: [AGENTS.md](../AGENTS.md) §4 Definition of Done · [GOAL.md](../GOAL.md)  
**Audience**: Engineers/operators and vibe coders

This file is the short answer to “is the harness done?”  
It is **not** a substitute for the authority documents. Runtime behavior must still match AGENTS.md.

---

## 1. Done for supported tasks (fixtures)

For the **fixture** task class (`fixtures/fix_add`, `always_fail_ci`, `over_loc`), the harness meets AGENTS.md §4:

| # | Requirement | Evidence on `main` |
|---|-------------|-------------------|
| 1 | Establish applicable authority | `resolve_authority` (fixture path must exist) |
| 2 | Constrain authorized scope | Disposable `WorkspaceSandbox`; path escape rejected |
| 3 | Produce or obtain an implementation | `AgentProvider` → harness-owned `apply_proposal` |
| 4 | Independently verify outcome + invariants | Net LOC, `py_compile`, workspace `pytest`, evidence ledger |
| 5 | Reject unsupported completion claims | `decide` reads ledger only — never provider text |
| 6 | Emit evidence for accept/reject | Trajectory + `artifacts/runs/<id>/run.json` |

**Proven outcomes**

- **ACCEPT** — product-code repair (`fix_add`) with mandatory `tests_pass`  
- **HUMAN_HANDOFF** — two CI failures (`always_fail_ci`)  
- **FAILED** — net LOC over budget (`over_loc`)

**Suite**: `pytest` **73 passed** (CLI v1 included).

**Operator UX (CLI v1)** — does not change authority:

- `.specialized-harness.yaml` defaults  
- Short form: `specialized-harness run fix_add`  
- Human summary by default; `--json` opt-in  
- Provider switch: config / `--provider` / env (`scripted` \| `http`)

---

## 2. Explicitly deferred (design intent, not shipped)

| Item | Why deferred |
|------|----------------|
| Multi-model routing | Eval corpus still thin |
| Pareto / offline workflow search | Eval corpus still thin |
| Full Code Maintenance Loop | Needs post-merge repo lifecycle |
| Credentialed remote git + PR creation | `push` is local-commit only; remote reported skipped |
| Selective path-based CI | Example overlay only under `configs/` |
| Real monorepo task contracts | Authority still fixture-directory shaped |
| Claude Code / other SDK providers | Optional future `AgentProvider`; not required for fixture Done |
| TUI / editor UI | CLI is primary surface after v1 cleanup |
| Direct LLM commits to `main` | **Forbidden** — PRs only; human merge (AGENTS.md §8) |

---

## 2b. Repository governance (this repo)

LLMs and agents **must not** commit or merge to `main`. They open pull requests only. **Only a human** (owner @Lvvphole or designated reviewer) may merge to `main`. See AGENTS.md §8, CONSTRAINTS.md, SECURITY.md.

Building deferred product features before more eval evidence would violate the **Minimum Sufficient Harness Principle** (ECONOMICS.md).

---

## 3. What “Done” does *not* mean

- The model is **not** the authority.  
- A chat UI declaring success is **not** Done.  
- Authority documents describing a capability is **not** the same as shipped, tested behavior.  
- Cost-optimal multi-model routing is **not** claimed without reproducible evals (GOAL.md).

---

## 4. Next product moves (when justified)

1. Keep docs/README honest when the suite or CLI changes.  
2. Generalize **authority resolution** beyond fixture directories only when a real task brief / monorepo path is required.  
3. Admit new providers or loops only when they improve correctness, containment, or Cost per Verified Correct Outcome with evidence.

---

## 5. Pointers

| Doc | Role |
|-----|------|
| [AGENTS.md](../AGENTS.md) | Behavioral contract + harness-level DoD + §8 repo write authority |
| [GOAL.md](../GOAL.md) | North-star workflow optimization |
| [README.md](../README.md) | Install, CLI quick start, sprint history |
