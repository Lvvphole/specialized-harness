# Eval #6 — Real-tree live model on Software-Factory `examples/demo-target`

**Date**: 2026-08-09  
**Authority**: AGENTS.md · GOAL.md · STATUS.md · OBSERVABILITY.md  
**Run id**: `7a7c8344-cf3f-4726-b6a8-776ca031abd6`  
**Artifact**: [`EVAL_006_run.json`](EVAL_006_run.json) (paths redacted; full trajectory preserved)

## Design

| Axis | Value |
|------|--------|
| Target | External tree: Software-Factory `examples/demo-target` (not a harness sample) |
| Provider | `HttpAgentProvider` (live OpenAI) |
| Task brief | Fix `add`: `a - b` → `a + b` in `src/calculator/__init__.py`; leave other paths alone |
| Blueprint | `blueprints/standard-coding.yaml` |

## Outcome (harness gates)

| Field | Value |
|-------|--------|
| **final_status** | **ACCEPT** |
| claims | `loc_within_budget` PASS (`net_loc=12`); `syntax_clean` PASS; `tests_pass` PASS (2 passed) |
| trajectory_len | 9 |
| Isolation | Source tree remained broken until human apply (sandbox-only mutation) |

## Contract honesty (Codex P1)

Harness **ACCEPT** means: mandatory ledger claims passed — especially **workspace pytest green**. It does **not** mean an exact one-line diff was proven.

- Task brief asked for minimal text change ("all other text identical").
- Recorded `net_loc=12` is inconsistent with a pure one-token operator swap under `measure_net_loc` (one remove + one add ≈ 2). Likely causes: full-file rewrite and/or CRLF→LF normalization on Windows source.
- There is **no** exact-diff / semantic-minimal-change gate in the shipped harness. Tests + syntax + LOC budget are the gates that fired.
- This eval records **real-tree live-model ACCEPT under independent verification**, not proof of minimal-edit discipline.

Do not treat EVAL_006 as evidence that an exact-change policy exists or passed.

## Authority check

- Provider returned mutations only; no success declaration from the model.
- ACCEPT decided solely by ledger + workspace pytest.
- Trajectory complete (AGENTS.md supporting invariant 9).

## Reproduce (operator)

```bash
# terminal 1
python3 scripts/live_propose_server.py   # mode=openai

# terminal 2
specialized-harness run \
  --provider http --provider-url http://127.0.0.1:8765 \
  --repo /path/to/Software-Factory/examples/demo-target \
  --task "Read src/calculator/__init__.py first. Change only the return of add from (a - b) to (a + b). Keep the mul function and all other text identical. Do not touch tests, conftest, or any other path." \
  --profile code-change --language python \
  --runs-dir artifacts/runs --json
```

Redact personal paths before committing any new run artifact.
