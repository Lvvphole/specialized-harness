# Writing Style & Output Standards

All structured outputs produced by this harness (trajectory events, PR descriptions, handoff summaries, plan artifacts) must conform to the following standards.

## General Rules

- Precise and factual. No speculation, motivational language, or filler.
- Prefer concrete diagnostics over restated problem statements.
- When given failure context (lint output, test failures), address the concrete items provided.
- Keep PR titles and bodies consistent with the target monorepo’s existing conventions.

## Trajectory Events

- Must contain every required field defined in OBSERVABILITY.md.
- `error` fields, when present, must quote or closely paraphrase the underlying diagnostic.
- `metadata` may contain additional structured data but must not be used to hide required information.

## Pull Request Descriptions

- Summary of what changed and why (derived from the plan and the actual diff).
- Explicit reference to the trajectory identifier.
- Checklist of quality gates that passed (local lint, selective CI).
- No claims about correctness beyond what the gates have verified.

## Human Handoff Records

- Clear statement that the second CI round failed or a hard limit was reached.
- Link to the full trajectory.
- List of remaining unresolved diagnostics.
- No recommendation that the agent should be re-run without human inspection of the trajectory.

These standards are enforced by review of sampled trajectories and by the regression suite.
