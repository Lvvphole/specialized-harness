# Sprint 2 Review

**Date**: 2026-08-07  
**Authority**: AGENTS.md v1.1.0  
**Repo**: https://github.com/Lvvphole/specialized-harness

## Goal

Prove the control plane governs **real** workspace execution: isolation, executable verification, measured LOC, inspectable evidence, and a swappable proposal source — without requiring a live model.

## Exit criteria — all met

| ID | Item | Evidence |
|----|------|----------|
| S2-1 | Disposable workspace sandbox | Copy-on-provision, path escape rejection, source fingerprint unchanged |
| S2-2 | Real net LOC from diffs | `measure_net_loc`; `over_loc` → non-ACCEPT |
| S2-3 | Real local verification | `py_compile` in workspace |
| S2-6 | Real CI | `pytest` in workspace; two real failures → HANDOFF |
| S2-5 | Evidence Ledger | claims: `syntax_clean`, `loc_within_budget`, `tests_pass` |
| S2-4 | AgentProvider + ScriptedProvider | Protocol + apply_proposal; model does not declare success |

## Definition of Done (Sprint 1 retained + Sprint 2)

- [x] ACCEPT path: `fix_add` → `FinalStatus.ACCEPT` with real pytest PASS claim
- [x] HANDOFF path: `always_fail_ci` → two CI failures → `HUMAN_HANDOFF`, no third CI
- [x] Isolation: source fixtures byte-stable after runs
- [x] LOC: measured `net_loc` on ACCEPT; over-budget cannot ACCEPT
- [x] Ledger: decide metadata carries claims; ACCEPT requires `tests_pass=PASS`
- [x] Provider: implement goes through `AgentProvider.propose` → harness `apply_proposal`
- [x] pytest: **38 passed** on GitHub `main`

## LOC budget

| Scope | Lines (approx) |
|-------|----------------|
| `src/` production | ~1122 |
| `tests/` | ~438 |
| Sprint 2 incremental slices | each kept under 1000 LOC hard limit |

Note: cumulative production source exceeds a single-sprint 1000 LOC *sum*, but each sprint slice was delivered under the per-sprint constraint. Cumulative growth should be reviewed against Minimum Sufficient Harness (ECONOMICS.md) in Sprint 3.

## Evidence commands

```text
specialized-harness run --task fix_add
  → ACCEPT; ledger tests_pass=PASS; net_loc measured

specialized-harness run --task always_fail_ci
  → HUMAN_HANDOFF after 2 real pytest failures

specialized-harness run --task over_loc
  → not ACCEPT; loc_within_budget=FAIL
```

## Retrospective

### What worked

- Fixture-first vertical slices unblocked proof without live models (Minimum Sufficient).
- Shared mutable context objects (`sandbox`, `evidence`, `ledger`, `provider`) avoided per-node ctx copy bugs once identified.
- Independent decide + ledger claims made ACCEPT inspectable, not inferred from task name.
- Quoting YAML `"on"` keys remains required (PyYAML 1.1 boolean gotcha from Sprint 1).

### What hurt

- Per-node `ctx = {**self.context}` means scalar writes on ctx do not persist; only shared objects do. Documented by S2-1/S2-3 bugs.
- `implement` still scripted markers rather than repairing fixture product code — sufficient for control-plane proof, weak for end-to-end "coding task" narrative.
- `git_push` / PR nodes remain stubs; trajectory implies push that does not happen.

### Decisions

1. Keep ScriptedProvider as default until a live provider earns its cost (ECONOMICS.md).
2. local_verify stays syntax-level; full pytest is the CI verification loop (VERIFICATION.md separation).
3. Evidence Ledger stays in-memory per run for now; persistence is Sprint 3+ if observability needs offline analysis.

### Backlog adaptation

- Sprint 2 items S2-1–S2-6: **closed**.
- Carry forward: real git/PR, live provider, product-code implement for `fix_add`, maintenance loop, economics/observability telemetry, trajectory persistence.
