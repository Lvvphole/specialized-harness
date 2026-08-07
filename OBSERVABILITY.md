# OBSERVABILITY.md — Harness Observability, Evals & Metrics

**Status**: Production Authority  
**Version**: 1.0.0  
**Authority Rank**: Parallel to CONSTRAINTS.md, VERIFICATION.md, and ECONOMICS.md; subordinate only to AGENTS.md  
**Aligned With**: AGENTS.md v1.1.0, VERIFICATION.md v1.1.0, ECONOMICS.md v1.0.0

---

## 1. Purpose

The authoritative layer defines what must be true.  
The verification layer establishes whether a particular change is true.  
The economics layer governs the cost of establishing it.  
The observability layer answers a different question:

> How is the harness actually performing over time, under real workloads, and how do we know whether it is improving, degrading, drifting, or wasting resources?

Verification makes a decision about a candidate change.  
Observability measures the **system that keeps making those decisions**.

**Canonical definition**

> The Observability Layer exists to capture sufficient structured evidence about every material harness execution so that correctness, reliability, verification effectiveness, cost, latency, failure behavior, and drift can be measured, reconstructed, compared, and improved over time.

In simpler terms:

> Authority tells us what good is. Verification determines whether one result is good. Observability tells us whether the system is consistently producing good results.

---

## 2. Canonical Pipeline

```text
AUTHORITATIVE LAYER
What must be true?
        │
        ▼
CODING / AGENTIC EXECUTION
        │
        ▼
VERIFICATION LAYER
Is this candidate actually correct?
 ├ Agentic Loop
 ├ CI Loop
 └ Maintenance Loop
        │
        ▼
ACCEPT / REJECT
        │
        ▼
─────────────────────────────────────
        OBSERVABILITY LAYER
─────────────────────────────────────
Measure across every run:
 • correctness
 • failures
 • verification
 • trajectories
 • retries
 • latency
 • tokens
 • cost
 • model routing
 • tool usage
 • CI outcomes
 • drift
 • maintenance
        │
        ▼
EVALS + METRICS + TREND ANALYSIS
        │
        ▼
ECONOMIC / ENGINEERING DECISIONS
        │
        ▼
ADAPTATION
What should we add, retain, modify,
make conditional, or remove?
```

---

## 3. Four Distinct Concepts

These must not be collapsed.

| Concept | Role |
|---------|------|
| **Observability** | Produces the structured evidence |
| **Evals** | Interpret evidence against defined claims |
| **Metrics** | Quantify the result so performance can be compared |
| **External benchmarks** (e.g. SWE-bench) | Calibrate against standardized tasks; never replace repository-specific evals or authoritative acceptance criteria |

**Evals (canonical)**

> Evals exist to convert desired system properties into repeatable measurement contracts that determine whether the model-plus-harness system actually exhibits those properties under defined conditions and budgets.

**Metrics (canonical)**

> Metrics exist to quantify the observable outcomes of those evals so that performance, reliability, economics, and change over time can be compared objectively.

**External benchmarks (canonical)**

> External software-engineering benchmarks exist to calibrate the coding system against standardized real-world tasks and comparable systems; they supplement, but never replace, repository-specific evals and authoritative acceptance criteria.

SWE-bench score must not become the objective function of this harness. It is external calibration. Project-specific evals answer the more important question: how capable is this harness at maintaining *our* repositories under *our* authority, architecture, verification rules, economic constraints, and failure tolerance.

---

## 4. Eval Structure

Every eval is a measurement contract:

```text
CLAIM
"What property do we believe the harness has?"
        ↓
TASK DISTRIBUTION
"Under what situations should this property hold?"
        ↓
MEASUREMENT
"What observable signals establish it?"
        ↓
SCORING
"What constitutes success/failure?"
        ↓
BUDGET
"How many attempts, tokens, tools, time and dollars?"
        ↓
VALIDITY
"Could the result be misleading?"
        ↓
TREND
"Is performance improving, stable or degrading?"
```

Example:

```yaml
eval: repository_issue_resolution
claim:
  harness can correctly resolve bounded repository issues
task_set: [bug_fixes, regression_fixes, api_changes, dependency_changes]
success:
  authoritative_requirements_satisfied: true
  required_tests_pass: true
  protected_invariants_preserved: true
  no_unapproved_scope_expansion: true
measure:
  - resolved_rate
  - first_pass_resolution_rate
  - regression_rate
  - verifier_false_accept_rate
  - retries
  - wall_clock_time
  - total_tokens
  - total_cost
validity:
  fixed_environment: true
  pinned_model: true
  fixed_harness_version: true
```

---

## 5. Three Classes of Evals

### 5.1 Capability Evals

> Can the coding system solve the engineering problem at all?

Includes SWE-bench and similar standardized tasks.

Metrics (illustrative):

```text
Resolution Rate
Task Completion Rate
Patch Applicability Rate
Compile Success Rate
Test Pass Rate
Fail-to-Pass Rate
Pass-to-Pass Preservation
Correct Localization Rate
Correct File Selection
Tool Success Rate
```

Primary SWE-bench-style headline:

\[
\text{Resolution Rate} = \frac{\text{Resolved Instances}}{\text{Submitted Instances}}
\]

### 5.2 Harness Effectiveness Evals

> How much better does the harness make the model?

Requires a baseline:

```text
MODEL ALONE  vs.  MODEL + HARNESS
```

Metrics (illustrative):

```text
Correct Outcome Rate
First-Pass Correct Rate
False Acceptance Rate
False Rejection Rate
Regression Escape Rate
Invariant Violation Rate
Architecture Violation Rate
Scope Violation Rate
Verification Detection Rate
Recovery Rate
Retry Rate
Human Escalation Rate
Agentic Verification Yield
CI Verification Value
```

Key delta:

\[
\Delta\text{Correctness} = COR_{\text{harness}} - COR_{\text{baseline}}
\]

This number, combined with cost, determines whether a control is economically justified.

### 5.3 Operational / Economic Evals

> At what system cost are we obtaining that correctness?

Metrics (illustrative):

```text
Input / output / total tokens
Prompt-cache and result-cache hit rates
Model calls / verifier calls / tool calls per task
CI executions and duration
Retry count and loop iterations
Wall-clock latency
Time to first useful action / time to verified completion
Inference cost / verification cost / CI cost / total task cost
Cost per successful task
Cost per verified correct outcome
Human intervention rate and review minutes
Context utilization and retrieval volume
Escalation frequency and model-routing distribution
```

Primary economic metric:

\[
\boxed{
\text{Cost Per Correct Outcome}
=
\frac{\text{Total Harness Cost}}{\text{Verified Correct Outcomes}}
}
\]

---

## 6. Verification-Quality Evals

The verifier itself can fail. Two highest-severity classes:

**False Acceptance Rate**

\[
FAR = \frac{\text{Incorrect Changes Accepted}}{\text{Incorrect Changes Presented}}
\]

Damages correctness and reliability.

**False Rejection Rate**

\[
FRR = \frac{\text{Correct Changes Rejected}}{\text{Correct Changes Presented}}
\]

Wastes tokens, CI cycles, agent iterations, time, human attention, and money.

Verifier quality is discrimination, not merely “how many errors were caught.”

---

## 7. Per-Loop Observability

### 7.1 Agentic Verification Loop

For each invocation:

```text
Agentic verifier invoked?
  ├── discovered real defect?
  ├── caused corrective change?
  ├── merely repeated CI finding?
  ├── false alarm?
  └── changed final outcome?
```

**Agentic Verification Yield**

\[
\text{Agentic Verification Yield}
=
\frac{\text{Material Defects Found Only Agentically}}{\text{Agentic Verifications Performed}}
\]

Directly informs economics: if a $0.20 reviewer catches one meaningful problem every 900 runs while deterministic checks already catch the rest, it should become risk-triggered, not universal.

### 7.2 CI Verification Loop

```text
CI pass rate
first-run CI pass rate
failure category
test flake rate
mean CI duration
CI reruns per task
failure → correction success rate
incremental vs full-suite savings
regression discovery rate
escaped regression rate
```

Distinguishes “CI is expensive because it is valuable” from “CI is expensive because the suite is poorly designed.”

### 7.3 Code Maintenance Loop

Long-horizon metrics:

```text
architecture / dependency violations over time
dependency age and vulnerability exposure
test flakiness
dead-code growth
technical-debt backlog
verification coverage
build / CI duration
code complexity
duplicate abstractions
exception / waiver / lint-suppression count
maintenance actions generated vs accepted
maintenance-induced regressions
```

The goal is not “how many refactors did the maintenance agent make?”  
The goal is: **how successfully is the maintenance system preventing measurable repository degradation at acceptable cost?**

---

## 8. Drift and Lineage

Every material run must record lineage:

```text
model version
harness version
prompt / instruction version
tool versions
repository commit
verification-policy version
eval-set version
seed (where supported)
reasoning configuration
```

Repeated evals then measure:

```text
Outcome Drift
Behavioral Drift
Cost Drift
Latency Drift
Verification Drift
Routing Drift
```

Without lineage, a drop from 94% → 89% correctness cannot be attributed to model, prompt, tool, retrieval, verification, repository, or test-distribution change.

---

## 9. Evidence Requirements

Every material node execution must emit a structured trajectory / evidence event containing at minimum:

- node_id, node_type, start_ts, end_ts, exit_status
- token usage (if agentic)
- artifacts produced or modified
- evidence references (tests, checks, authority sources)
- cost and latency signals
- model / routing identifiers
- links into the Evidence Ledger for verification claims

Incomplete trajectories are infrastructure failures.

---

## 10. Adaptation

Observability + evals make the Minimum Sufficient Harness Principle executable:

```text
Evidence of performance / cost / drift
        ↓
Decide whether a model, verifier, rule, test,
retrieval strategy, loop, or control should be:
  - added
  - retained
  - modified
  - made conditional (risk-triggered)
  - removed
```

Without this loop, economics remains philosophical.

---

## 11. Definition of Done for the Observability Layer

The observability layer is complete when the harness can:

1. Emit complete, structured trajectories for every material execution.
2. Support the three classes of evals (Capability, Harness Effectiveness, Operational/Economic) under fixed, versioned conditions.
3. Measure verifier discrimination (FAR, FRR) and per-loop yields.
4. Record full lineage so drift can be attributed.
5. Produce Cost Per Correct Outcome and ΔCorrectness against a defined baseline.
6. Feed empirical evidence into control admission, runtime admission, and the rational stopping rule (ECONOMICS.md).

---

## 12. Change Control

Changes to this document require:

- Explicit version update
- Confirmation that Observability, Evals, Metrics, and external benchmarks remain distinct
- Confirmation that SWE-bench (and similar) remain calibration tools, not the objective function
- Alignment with AGENTS.md, VERIFICATION.md, and ECONOMICS.md
