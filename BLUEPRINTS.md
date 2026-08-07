# BLUEPRINTS.md — Blueprint Specification

**Status**: Production Authority  
**Version**: 1.1.0  
**Aligned With**: AGENTS.md v1.1.0 and CONSTRAINTS.md v1.1.0

A Blueprint is the authoritative definition of a fixed-phase workflow. It declares the sequence of nodes, the conditions under which control moves from one node to the next, the tool surface available to each agentic node, and the policy counters that the engine must respect.

Blueprints exist to make the five questions answerable in a concrete, repeatable way: they encode how authority is resolved, how scope is constrained, how verification is performed, and how success is independently declared.

---

## 1. Blueprint Schema (Conceptual)

```yaml
apiVersion: specialized-harness/v1
kind: Blueprint
metadata:
  name: standard-coding
  description: >
    Governed implementation of a coding task under explicit authority,
    constrained scope, independent verification, and independent
    declaration of success.
  version: "1.1.0"

spec:
  policy:
    max_ci_rounds: 2
    max_agentic_recovery_attempts: 1
    max_net_loc: 1000
    default_agentic_timeout: 15m
    require_trajectory: true
    require_authority_resolution: true

  nodes:
    - id: resolve_authority
      type: deterministic
      handler: resolve_authority
      description: Establish task contract, applicable specs, tests, and policies

    - id: constrain_scope
      type: deterministic
      handler: constrain_scope
      description: Bind permitted files, tools, and side effects

    - id: provision
      type: deterministic
      handler: provision_sandbox

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

    - id: local_verify
      type: deterministic
      handler: run_local_verification
      description: Lint, type-check, contract validation; apply autofixes

    - id: push
      type: deterministic
      handler: git_push

    - id: ci_round
      type: deterministic
      handler: selective_ci_and_verify_outcome

    - id: fix_ci
      type: agentic
      handler: fix_ci_failures
      tools: [read_file, write_file, run_local_command, get_test_output]
      system_prompt_ref: prompts/fix_ci.md
      budget:
        max_tokens: 48000
        timeout: 15m

    - id: decide
      type: deterministic
      handler: decide_accept_or_handoff
      description: Independent declaration of success or explicit human handoff

  edges:
    - from: resolve_authority
      to: constrain_scope
      on: success

    - from: constrain_scope
      to: provision
      on: success

    - from: provision
      to: plan
      on: success

    - from: plan
      to: implement
      on: success

    - from: implement
      to: local_verify
      on: success

    - from: local_verify
      to: push
      on: success
    - from: local_verify
      to: implement
      on: failure
      when: recovery_attempts < max_agentic_recovery_attempts

    - from: push
      to: ci_round
      on: success

    - from: ci_round
      to: decide
      on: success
    - from: ci_round
      to: fix_ci
      on: failure
      when: ci_rounds < max_ci_rounds
    - from: ci_round
      to: decide
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
- Responsible for authority resolution, constraint, verification, and independent decision.

### Agentic Node
- Handler prepares context, calls the model, processes tool calls, and returns a structured `NodeResult`.
- Tool surface is the only tools the model may see for that node.
- System prompt is loaded from the referenced file.
- The model may propose; it may not declare success or expand its own authority.

---

## 3. Edge Conditions

Edges are evaluated in order. The first matching edge is taken. Supported predicates:

- `on: success | failure`
- `when: <expression over policy counters and node results>`

The engine evaluates the `when` clause against a small, well-defined context (ci_rounds, recovery_attempts, net_loc, last_node_status, etc.). Arbitrary code is not permitted in edge conditions.

---

## 4. Required Blueprints for a Production Deployment

At minimum a production deployment must ship:

1. `standard-coding` — governed implementation under explicit authority, constrained scope, and independent verification.
2. `flaky-test-fix` — specialized for repairing intermittent tests while preserving the same authority and decision invariants.
3. `human-handoff` — terminal blueprint used when policy limits are exhausted.

Additional blueprints may be added for domain-specific workflows provided they respect the hard invariants in AGENTS.md and CONSTRAINTS.md (including independent declaration of success and the 1,000 LOC limit).

---

## 5. Validation

- Every blueprint must be validated against the schema before the engine will load it.
- A static analysis pass must confirm that no path can reach a third CI round.
- A static analysis pass must confirm that every agentic node declares an explicit tool surface.
- A static analysis pass must confirm that authority resolution and independent decision nodes are present on every accepting path.
- Blueprint regression tests execute the blueprint against recorded fixtures and assert final outcomes and evidence emission.
