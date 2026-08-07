# AGENTS.md — Authority Document for the Specialized Agentic Harness

**Status**: Production Authority  
**Version**: 1.1.0  
**Last Updated**: 2026-08-06  
**Scope**: Authoritative coding-agent harness — deterministic governance of probabilistic generation

This document is the primary behavioral authority for any agent operating inside this harness. All other documents (ARCHITECTURE.md, CONSTRAINTS.md, VERIFICATION.md, BLUEPRINTS.md, OBSERVABILITY.md, SECURITY.md) are subordinate to the invariants defined here.

---

## 1. Purpose

An authoritative coding-agent harness exists to ensure that only repository-conformant, independently verified changes can cross the boundary from model-generated proposal to accepted implementation, while achieving that assurance with the minimum sufficient latency, cost, complexity, and new failure surface.

The coding model is **not** the authority.  
The repository, specifications, invariants, tests, policies, and acceptance rules **are** the authority.  
The harness exists to enforce that boundary.

### Required Transformation

```text
Probabilistic proposal
        → constrained execution
        → objective verification
        → authoritative acceptance or rejection
```

The harness’s job is not primarily to make the model smarter.  
Its job is to make incorrect behavior hard to commit, easy to detect, and impossible to declare complete without evidence.

### The Five Questions the Harness Must Answer

1. **What is actually required?**  
   Resolve the authoritative source of truth: task contract, repository state, specifications, ADRs, interfaces, tests, policies, and applicable constraints.

2. **What is the agent allowed to change?**  
   Bound scope, permissions, files, commands, tools, side effects, and authority. The model may propose; it does not get to redefine requirements.

3. **Did the implementation preserve the system’s invariants?**  
   Compile, type-check, lint, test, validate schemas/contracts, inspect diffs, check security/safety rules, and enforce repository-specific invariants.

4. **Did the requested outcome actually occur?**  
   Verification must measure the desired state, not merely whether the agent produced code or whether a command exited 0.

5. **Who gets to declare success?**  
   Not the model that wrote the code. Completion is declared by deterministic checks wherever possible, with explicit escalation when judgment remains necessary.

### Architectural Separation

```text
AUTHORITATIVE SOURCES
repo + specs + tests + policies + task contract
              │
              ▼
        HARNESS / GOVERNOR
resolve → constrain → execute → verify → decide
              │
              ▼
        CODING MODEL
     proposes implementation
              │
              ▼
        REPOSITORY CHANGE
              │
              ▼
      INDEPENDENT EVIDENCE
 tests + static checks + diff + runtime evidence
              │
              ▼
       ACCEPT / REJECT
```

### Value Function

A strong authoritative harness optimizes approximately:

\[
\text{Harness Value} = \frac{\text{Correct Accepted Outcomes} \times \text{Failure Containment}}{\text{Latency} \times \text{Cost} \times \text{Added Failure Surface}}
\]

Every control must earn its place by measurably improving correctness, containment, or authority enforcement. The harness itself must not become a larger, slower, or more expensive failure surface than the coding task it governs.

---

## 2. Core Invariants (Non-Negotiable)

These invariants are ordered by the five questions the harness must answer. They override any lower-level document or runtime configuration.

### 2.1 Authority Resolution
The harness must deterministically establish the applicable source of truth for every supported task. Ambiguous or missing authority is treated as a blocking condition, not as permission for the model to invent requirements.

### 2.2 Scope and Permission Bounding
The agent may change only what it has been explicitly authorized to change. The model cannot expand its own tool surface, redefine the task contract, or claim authority over policies, tests, or acceptance rules.

### 2.3 Invariant Preservation
Protected system invariants (compilation, types, lint rules, contracts, schemas, security rules, and repository-specific constraints) are enforced by deterministic mechanisms. Model statements that contradict deterministic results are ignored for control-flow purposes.

### 2.4 Outcome Verification
Success is measured against the desired state defined by the authoritative sources. “Code was produced,” “the command exited 0,” or “the model claims the task is done” are insufficient. Verification is performed by the hybrid verifier defined in VERIFICATION.md.

### 2.5 Independent Declaration of Success
The model that generated the implementation does not get to declare completion. Completion is declared only by:
- deterministic checks that have passed, or
- explicit human escalation when residual judgment is required.

### 2.6 Minimum Sufficient Control Surface
Every additional control, node, tool, or policy layer must demonstrably improve correctness, containment, or authority enforcement. Complexity that does not improve the value function is rejected.

### Supporting Process Invariants

6. **Deterministic gates are absolute.**  
   Quality gates (lint, type-check, test selection, policy enforcement, git operations) are implemented as deterministic nodes. The model cannot skip, reorder, or reinterpret them.

7. **Hard iteration limits on expensive feedback.**  
   At most two CI rounds are permitted per run. After the second CI round, control is surrendered. No further agentic work is allowed on that run.

8. **Isolation boundary.**  
   All execution occurs inside disposable, non-networked, non-production sandboxes. The agent receives full local permissions inside the sandbox and zero permissions outside it.

9. **Trajectory completeness.**  
   Every node execution (agentic or deterministic) must emit a structured trajectory record. Incomplete trajectories are treated as infrastructure failures.

10. **Sprint size limit.**  
    Net lines of code changed in a single sprint/run must not exceed 1,000. Exceeding this limit forces human handoff or rejection.

---

## 3. Agent Behavior Rules

### 3.1 What the Agent May Do
- Propose implementations inside designated agentic nodes.
- Read and write files within the authorized scope.
- Call tools that have been explicitly scoped to the current node.
- Request additional context via the approved tool surface.
- Respond to concrete failure diagnostics provided by deterministic gates.

### 3.2 What the Agent Must Never Do
- Redefine requirements, acceptance criteria, or the task contract.
- Expand its own permissions, tool surface, or scope.
- Skip, disable, reorder, or reinterpret a deterministic gate.
- Declare the task complete.
- Continue working after the second CI round or after a hard policy limit has been reached.
- Emit unstructured or incomplete trajectory data.
- Treat any model-generated statement as authoritative over a deterministic result.

### 3.3 Failure Handling
- Recoverable deterministic failures are routed to a designated recovery path or to human handoff according to the blueprint.
- Exhaustion of iteration limits, scope limits, or LOC limits forces immediate human handoff.
- Unsupported claims of completion are rejected; the trajectory must record the rejection reason.

---

## 4. Definition of Done (Harness Level)

Given a supported coding task, the harness can:

1. Deterministically establish the applicable authority,
2. Constrain execution to the authorized scope,
3. Produce or obtain an implementation,
4. Independently verify the required outcome and protected invariants (see VERIFICATION.md),
5. Reject unsupported claims of completion, and
6. Emit sufficient evidence to explain why the change was accepted or rejected.

A run is complete only when the above conditions are met or when an explicit human-handoff record has been emitted after a hard limit was reached. The model does not declare completion.

---

## 5. Writing Style & Communication Standards

- Trajectory records, PR descriptions, and handoff summaries must be precise, factual, and free of speculation.
- When given failure context, the agent addresses the concrete diagnostics provided.
- No motivational language, filler, or restatement of the problem is permitted in structured outputs.
- Evidence of acceptance or rejection must be explicit and inspectable.

---

## 6. Model Independence

This harness is deliberately model-agnostic. Any model that can follow tool-calling conventions and produce structured outputs may be used. Reliability guarantees derive from the harness (authority resolution, constraint, verification, and independent decision), not from model capability.

---

## 7. Authority Hierarchy

1. This file (AGENTS.md)
2. CONSTRAINTS.md and VERIFICATION.md (parallel; both subordinate only to AGENTS.md)
3. ARCHITECTURE.md
4. BLUEPRINTS.md + individual blueprint definitions
5. Runtime configuration and monorepo-specific overlays

Conflicts are resolved by the higher document. Runtime code must refuse to start if a lower document contradicts an invariant in this file.

---

## 8. Change Control

Changes to this document require:
- Explicit update of the version number
- Review against the regression suite of blueprints
- Confirmation that no core invariant (especially the five questions and independent declaration of success) has been weakened

This document is the contract between the harness authors and any downstream consumer.
