# Sprint 1 Review

## Goal
Prove one end-to-end ACCEPT path and one HUMAN_HANDOFF path against fixture repositories.

## Exit criteria — all met
- [x] ACCEPT path: fixture `fix_add` → FinalStatus.ACCEPT, trajectory includes resolve→…→decide
- [x] HUMAN_HANDOFF path: fixture `always_fail_ci` → 2 CI failures → HUMAN_HANDOFF, no third CI
- [x] PolicyViolation on third CI attempt
- [x] Trajectory events carry node_id, node_type, exit_status, sequence
- [x] Sprint LOC: ~544 production + ~117 tests (< 1000)

## Evidence
```
specialized-harness run --task fix_add
  final_status=ACCEPT trajectory_len=9

specialized-harness run --task always_fail_ci
  final_status=HUMAN_HANDOFF trajectory_len=12 nodes include ci_round x2
```
pytest: 10 passed

## Retrospective
- PyYAML 1.1 treats bare key `on` as boolean; blueprints must quote `"on"` or engine must accept True key.
- Fixture-driven handlers were sufficient to prove control plane without live models (Minimum Sufficient for this sprint).
- Next sprint: real sandbox, real local verification, Evidence Ledger, replace stub agentic nodes with provider interface.

## Backlog adaptation
- B1.1–B1.5 partially done (engine, loader, CLI, trajectory, policy)
- B2/B3 still stubs
- B4.1–B4.3 done for fixtures + accept/handoff tests
