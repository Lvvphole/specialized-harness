# BLUEPRINTS.md — Blueprint Specification

**Status**: Production Authority  
**Version**: 1.0.0

A Blueprint is the authoritative definition of a fixed-phase workflow. It declares the sequence of nodes, the conditions under which control moves from one node to the next, the tool surface available to each agentic node, and the policy counters that the engine must respect.

---

## 1. Blueprint Schema (Conceptual)

```yaml
apiVersion: specialized-harness/v1
kind: Blueprint
metadata:
  name: standard-coding
  description: One-shot coding task from specification to CI-passing PR
  version: "1.0.0"

spec:
  policy:
    max_ci_rounds: 2
    max_agentic_recovery_attempts: 1
    default_agentic_timeout: 15m

  nodes:
    - id: provision
      type: deterministic
      handler: provision_sandbox

    - id: hydrate
      type: deterministic
      handler: hydrate_context

    - id: plan
      type: agentic
      handler: plan
      tools: [read_file, list_dir, search_code, get_ticket]
      system_prompt_ref: prompts/plan.md
      budget:
        max_tokens: 32000
        timeout: 10m

    - id: implement
      type: agentic
      handler: implement
      tools: [read_file, write_file, list_dir, search_code, run_local_command]
      system_prompt_ref: prompts/implement.md
      budget:
        max_tokens: 64000
        timeout: 20m

    - id: local_lint
      type: deterministic
      handler: run_local_linters

    - id: push
      type: deterministic
      handler: git_push

    - id: ci_round
      type: deterministic
      handler: selective_ci

    - id: fix_ci
      type: agentic
      handler: fix_ci_failures
      tools: [read_file, write_file, run_local_command, get_test_output]
      system_prompt_ref: prompts/fix_ci.md
      budget:
        max_tokens: 48000
        timeout: 15m

    - id: finalize
      type: deterministic
      handler: create_pull_request

  edges:
    - from: provision
      to: hydrate
      on: success

    - from: hydrate
      to: plan
      on: success

    - from: plan
      to: implement
      on: success

    - from: implement
      to: local_lint
      on: success

    - from: local_lint
      to: push
      on: success
    - from: local_lint
      to: implement
      on: failure
      when: recovery_attempts < max_agentic_recovery_attempts

    - from: push
      to: ci_round
      on: success

    - from: ci_round
      to: finalize
      on: success
    - from: ci_round
      to: fix_ci
      on: failure
      when: ci_rounds < max_ci_rounds
    - from: ci_round
      to: finalize
      on: failure
      when: ci_rounds >= max_ci_rounds

    - from: fix_ci
      to: push
      on: success
```

---

## 2. Node Types

### Deterministic Node
- Handler is ordinary code.
- Must be side-effect controlled and unit-testable.
- Returns a structured `NodeResult`.
- Never invokes a language model.

### Agentic Node
- Handler prepares context, calls the model, processes tool calls, and returns a structured `NodeResult`.
- Tool surface is the only tools the model may see for that node.
- System prompt is loaded from the referenced file and may be further parameterized by the blueprint.

---

## 3. Edge Conditions

Edges are evaluated in order. The first matching edge is taken. Supported predicates:

- `on: success | failure`
- `when: <expression over policy counters and node results>`

The engine evaluates the `when` clause against a small, well-defined context (ci_rounds, recovery_attempts, last_node_status, etc.). Arbitrary code is not permitted in edge conditions.

---

## 4. Required Blueprints for a Production Deployment

At minimum a production deployment must ship:

1. `standard-coding` — the primary one-shot coding flow.
2. `flaky-test-fix` — specialized for repairing intermittent tests.
3. `human-handoff` — terminal blueprint used when policy limits are exhausted.

Additional blueprints may be added for domain-specific workflows (migrations, large refactors, documentation updates) provided they respect the hard constraints in AGENTS.md and CONSTRAINTS.md.

---

## 5. Validation

- Every blueprint must be validated against the schema before the engine will load it.
- A static analysis pass must confirm that no path can reach a third CI round.
- A static analysis pass must confirm that every agentic node declares an explicit tool surface.
- Blueprint regression tests execute the blueprint against recorded fixtures and assert final outcomes.
