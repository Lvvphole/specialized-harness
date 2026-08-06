# AGENTS.md — Authority Document for Specialized Agentic Harness

**Status**: Production Authority  
**Version**: 1.0.0  
**Last Updated**: 2026-08-06  
**Modeled On**: Stripe Minions / Blueprints architecture  
**Scope**: Deterministic-blueprint specialized coding harness for monorepos

This document is the primary behavioral authority for any agent operating inside this harness. All other documents (ARCHITECTURE.md, CONSTRAINTS.md, BLUEPRINTS.md) are subordinate to the invariants defined here.

---

## 1. Purpose

This harness exists to execute **one-shot, end-to-end coding tasks** with the following properties:

- The agent produces a complete pull request that has passed local quality gates and selective CI.
- Critical engineering steps are enforced by deterministic code, not by model judgment.
- The system is reusable across multiple monorepos and codebases with minimal configuration.
- Any capable model may be plugged in; the harness, not the model, guarantees process integrity.

The model is treated as a powerful but fallible worker. The harness is the supervisor that decides what must happen.

---

## 2. Core Invariants (Non-Negotiable)

1. **Deterministic gates are absolute.**  
   Linting, selective test execution, CI policy enforcement, git operations, and PR creation are implemented as deterministic nodes. The model cannot skip, reorder, or reinterpret them.

2. **Hard iteration limit on expensive feedback.**  
   At most two CI rounds are permitted. After the second CI round, control is surrendered to a human. No further agentic work is allowed on that run.

3. **Isolation boundary.**  
   All execution occurs inside disposable, non-networked, non-production sandboxes (devboxes). The agent receives full local permissions inside the sandbox and zero permissions outside it.

4. **Conditional context only.**  
   Agent rule files and tool scopes are applied conditionally by directory, file pattern, or explicit blueprint configuration. Unconditional global rules that apply to an entire large monorepo are forbidden.

5. **Trajectory completeness.**  
   Every node execution (agentic or deterministic) must emit a structured trajectory record. Incomplete trajectories are treated as infrastructure failures.

6. **Definition of Done is binary and code-enforced.**  
   A run is complete only when a PR exists that has passed the required local + CI gates (or has been explicitly marked for human handoff after the second CI failure). The model does not declare completion.

---

## 3. Agent Behavior Rules

### 3.1 What the Agent May Do
- Reason about the task inside designated agentic nodes.
- Read and write files inside the sandbox.
- Call tools that have been explicitly scoped to the current node.
- Request additional context via the approved MCP / tool surface.
- Propose code changes, plans, and fixes within the current agentic phase.

### 3.2 What the Agent Must Never Do
- Attempt to bypass, disable, or re-order a deterministic node.
- Request or assume network access, production credentials, or secrets outside the sandbox.
- Continue working after the second CI round has completed.
- Emit unstructured or incomplete trajectory data.
- Modify the blueprint definition or policy files during a run.
- Treat any model-generated statement as authoritative over a deterministic gate result.

### 3.3 Failure Handling
- When a deterministic node fails with a recoverable error, the engine routes control to a designated recovery agentic node (if one exists in the blueprint) or to human handoff.
- When an agentic node produces invalid tool calls or exceeds its budget, the node is terminated and the failure is recorded in the trajectory.
- After the second CI failure without autofix resolution, the run is marked `human_handoff` and the agent is stopped.

---

## 4. Writing Style & Communication Standards

- All trajectory records, PR descriptions, and handoff summaries must be precise, factual, and free of speculation.
- PR titles and descriptions follow the repository’s existing conventions (configured per monorepo).
- When the agent is given failure context (lint output, test failures), it must address the concrete diagnostics provided rather than re-deriving the problem from first principles.
- No motivational language, filler, or unnecessary restatement is permitted in structured outputs.

---

## 5. Model Independence

This harness is deliberately model-agnostic. Any model that can:
- Follow tool-calling conventions,
- Consume the provided system and node-level prompts,
- Produce structured outputs when required,

may be used. The reliability guarantees of the system derive from the blueprint engine and deterministic nodes, not from model capability.

---

## 6. Authority Hierarchy

1. This file (AGENTS.md)
2. CONSTRAINTS.md
3. ARCHITECTURE.md
4. BLUEPRINTS.md + individual blueprint definitions
5. Runtime configuration and monorepo-specific overlays

Conflicts are resolved by the higher document. Runtime code must refuse to start if a lower document contradicts an invariant in this file.

---

## 7. Change Control

Changes to this document require:
- Explicit update of the version number
- Review against the regression suite of blueprints
- Confirmation that no deterministic invariant has been weakened

This document is the contract between the harness authors and any downstream consumer.
