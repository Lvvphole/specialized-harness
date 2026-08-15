# STATUS.md — Done boundary (what is shipped vs deferred)

**Date**: 2026-08-15  
**Authority**: [AGENTS.md](../AGENTS.md) §4 Definition of Done · [GOAL.md](../GOAL.md)  
**Audience**: Engineers/operators and vibe coders

This file is the short answer to “is the harness done?”  
It is **not** a substitute for the authority documents. Runtime behavior must still match AGENTS.md.

---

## 1. Done for supported tasks

### Fixtures

For `fixtures/fix_add`, `always_fail_ci`, `over_loc`, the harness meets AGENTS.md §4.

### Repo mode (sample)

For `samples/repo_add` with `--repo` + task brief, **ACCEPT** is proven:

- Offline: ScriptedProvider + workspace pytest + ledger (isolation of the sample tree preserved).
- Live HTTP path (EVAL_001): rehearsal mode via `HttpAgentProvider` + multi-round tools → ACCEPT (run_id `a032ba27-838d-4a9f-ae7d-a12db2bc32b8`).
- Live model path (EVAL_002): real OpenAI (`gpt-4.1-mini`) via same provider → ACCEPT after 2 CI rounds (run_id `af60d7e1-8ca1-4d22-a2ac-cff01607eac3`; net_loc=3; tokens prompt 6522 / completion 401). See [docs/evals/](evals/).

`samples/repo_mul` (EVAL_003–005) and `samples/repo_stats` (EVAL_007–008) extend the same
contract to a second and third tree; `repo_stats` is the first sample that is a package
rather than a flat `app.py`, and the first whose bug is a boundary case rather than an
operator swap. `samples/repo_sub` (EVAL_009) adds offline meta-verification evidence
(unit red on source + ACCEPT + isolation + checker-qual floor).

**Proven outcomes**

- **ACCEPT** — fixture product-code repair (`fix_add`)
- **ACCEPT (repo mode, offline + live)** — `samples/repo_add` via `--repo` + brief
- **ACCEPT (repo mode, offline)** — `samples/repo_mul` via `--repo` + brief (EVAL_003; second sample)
- **ACCEPT (repo mode, live HTTP rehearsal)** — `samples/repo_mul` (EVAL_004; run_id `1baec317-bc15-4796-95cb-9105d315943c`)
- **ACCEPT (repo mode, live OpenAI)** — `samples/repo_mul` (EVAL_005; run_id `1897d3c1-a1f0-47dd-9795-3b588fc08886`; net_loc=3; total_ms 9427)
- **ACCEPT (repo mode, offline + live OpenAI)** — `samples/repo_stats` (EVAL_007 offline/rehearsal; **EVAL_008** live OpenAI run_id `046e1ec8-2c20-49b1-888e-4dd7a645255e`; net_loc=32; total_ms 16716; 3 tests). First package tree + non-operator bug class under real model.
- **ACCEPT (repo mode, offline + meta-verification)** — `samples/repo_sub` (EVAL_009; run_id `ecf8bfb4-6f4e-46a3-a7f4-81089395d49a`; net_loc=5; unit red on source + offline ACCEPT + isolation + checker-qual floor)
- **HUMAN_HANDOFF** — two CI failures (`always_fail_ci`)
- **FAILED** — net LOC over budget (`over_loc`)

**Suite**: offline eval contracts + checker qualification (see [VERIFICATION_VS_EVAL.md](VERIFICATION_VS_EVAL.md)).

**Operator UX**

```bash
specialized-harness run fix_add
specialized-harness run --repo samples/repo_add --task "Fix the broken add function"
specialized-harness run --repo samples/repo_stats --task "Fix the broken median function"
specialized-harness run --repo samples/repo_sub --task "Fix the broken subtract function"
# live path (requires propose server + optional OPENAI_API_KEY):
# see docs/evals/EVAL_001.md … EVAL_009.md
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
| Full arbitrary monorepo repair | Sample proven; general trees need broader live corpus |
| Claude Code / other SDK providers | Optional; not required for sample Done |
| TUI / editor UI | CLI primary |
| Direct LLM commits to `main` | Forbidden — PRs only (AGENTS.md §8) |
| promptfoo on ACCEPT path | Eval-only; never gates product ACCEPT |

---

## 2b. Repository governance

LLMs/agents open PRs only. **Only a human** (@Lvvphole or designate) merges to `main`.

---

## 3. What Done does *not* mean

- The model is not the authority.
- A chat UI declaring success is not Done.
- Authority text is not shipped behavior.
- A single sample task ACCEPT (even live) is not a claim of general monorepo competence.

---

## 4. Verification vs Eval (Sprint 8)

See [VERIFICATION_VS_EVAL.md](VERIFICATION_VS_EVAL.md).

| Layer | Question |
|-------|----------|
| Verification harness | Does this **candidate** satisfy the contract? |
| Eval harness | Is this **component** good enough to admit? |
| Checker qualification | Can this **checker** separate valid from invalid? |

Offline qualification for `syntax_clean` / `tests_pass` ships in `specialized_harness.evals`. **ACCEPT path unchanged.** promptfoo is eval-only if used later.

## 5. Next product moves (when justified)

1. Further corpus growth. Four samples: `repo_add` / `repo_mul` (live OpenAI EVAL_002 / EVAL_005); `repo_stats` (EVAL_007 offline+rehearsal, **EVAL_008 live OpenAI**); `repo_sub` (EVAL_009 offline meta-verification). Next: real-model on `repo_sub`, or a sample whose repair spans more than one file.
2. Selective CI / path policies when a monorepo demands it.
3. Admit controls only when they improve Cost per Verified Correct Outcome (incl. token profile under matched ACCEPT; OckBench / Gloaguen as calibration only).
