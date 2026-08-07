# ECONOMICS.md — Harness Engineering Economics

**Status**: Production Authority  
**Version**: 1.0.0  
**Authority Rank**: Parallel to CONSTRAINTS.md and VERIFICATION.md; subordinate only to AGENTS.md  
**Aligned With**: AGENTS.md v1.1.0, VERIFICATION.md v1.1.0

---

## 1. Purpose

The authoritative layer defines what must be true.  
The verifier layer establishes whether it is true.  
The economics layer answers a different question:

> What is the least expensive sufficient system that can achieve and sustain the required level of correctness, reliability, safety, and verification?

**Canonical definition**

> The economics of harness engineering exists to minimize the total lifecycle cost of producing and sustaining correct, safely accepted outcomes, subject to mandatory authority, reliability, safety, and verification requirements. It does so by admitting only controls whose marginal assurance value justifies their marginal cost and failure surface, selecting the cheapest sufficient execution and verification path for each task, and stopping once the authoritative evidence threshold has been satisfied.

**Desired state**

> Spend no more computation, latency, complexity, verification, or human attention than is necessary to reliably know that the result is correct.

This is different from simply minimizing token cost. A harness that saves $0.02 in model calls but causes more failures is economically worse. A harness that achieves 99.9% correctness at 10× the cost when 99% satisfies the product requirement may also be economically worse.

The economic problem is an **optimization under constraints**.

---

## 2. Core Economic Objective

\[
\boxed{\text{Minimize Total Cost of Correctness}}
\]

subject to:

\[
\begin{align*}
\text{CorrectOutcomeRate} &\ge C_{\min} \\
\text{FailureContainment} &\ge F_{\min} \\
\text{Safety} &= \text{mandatory constraints satisfied} \\
\text{AuthorityCompliance} &= 100\% \text{ for mandatory invariants} \\
\text{VerificationCoverage} &\ge V_{\min}
\end{align*}
\]

Mandatory safety, authority boundaries, and required reliability are **constraints around the optimization**, not weights that may be casually traded against cost.

```text
               MANDATORY FLOOR
                      │
        ┌─────────────┴─────────────┐
        │ correctness               │
        │ safety                    │
        │ authority                 │
        │ failure containment       │
        │ required verification     │
        └─────────────┬─────────────┘
                      │
              once floor is met
                      ▼
               OPTIMIZE FOR
                      │
       ┌──────────────┼──────────────┐
       ▼              ▼              ▼
      Cost          Latency       Complexity
       │              │              │
       └──────────────┼──────────────┘
                      ▼
             Minimum Sufficient
                  Harness
```

**Economics operates beneath the safety/reliability floor, not instead of it.**

---

## 3. Total Cost of Correctness

The unit of optimization is not cost per model call. It is the full cost of producing a trustworthy result:

\[
\text{Total Cost of Correctness} = C_m + C_v + C_i + C_l + C_h + C_f + C_o + C_d
\]

| Component | Meaning |
|-----------|---------|
| \(C_m\) | Model inference cost |
| \(C_v\) | Verification cost |
| \(C_i\) | Infrastructure / tool execution cost |
| \(C_l\) | Latency cost |
| \(C_h\) | Human-review / escalation cost |
| \(C_f\) | Expected failure and rework cost |
| \(C_o\) | Operational / maintenance complexity cost |
| \(C_d\) | Drift and new-failure-surface cost |

A $0.20 frontier-model call that produces a correct patch in one attempt can be cheaper than a $0.03 small model that triggers five retries, three verifier calls, CI, and human intervention. Likewise, spending an additional $0.05 on deterministic verification is economically excellent if it prevents a $500 engineering incident.

The harness optimizes **system economics**, not model economics alone.

---

## 4. Economic Harness Efficiency

\[
\boxed{
\text{Economic Harness Efficiency}
=
\frac{
\text{Correct Accepted Outcomes}
\times
\text{Failure Containment}
}{
\text{Total Cost of Correctness}
}
}
\]

This ratio must never be allowed to trade away mandatory safety or authority constraints. If a control protects a mandatory invariant, the harness cannot remove it solely because “removing it gives 8% better economics.”

---

## 5. Minimum Sufficient Harness Principle

> No harness capability should exist merely because it could improve performance. It should enter the harness only when the expected improvement in correctness, failure containment, safety, or economically meaningful efficiency exceeds the lifecycle cost and new failure surface it introduces, unless the capability is required by a mandatory constraint.

Every proposed control must justify itself by answering:

```text
What failure class does it address?
How often does that failure occur?
What is the consequence of that failure?
How much does the control reduce it?
Can deterministic verification solve it more cheaply?
Can one smaller verifier solve it?
How much latency does it add?
How many tokens does it add?
What operational complexity does it introduce?
What new failure modes does the control itself create?
How often will it run?
Can it run only on risk-triggered paths?
Does its marginal benefit justify its marginal cost?
```

Only then does the control earn admission.

---

## 6. Three Economic Questions the Layer Continuously Answers

### 6.1 What should exist? (Control admission)

Does this capability earn a permanent place in the harness?

### 6.2 What should run? (Runtime admission)

Even if the capability exists, does **this particular task** justify paying for it?

### 6.3 When should we stop? (Marginal verification value)

Once sufficient evidence exists, additional verification has diminishing economic value.

**Rational stopping rule**

> Stop adding verification when the authoritative evidence threshold has been satisfied and the expected value of another verification action is lower than its expected cost, unless a mandatory control remains unsatisfied.

Without this rule, agent loops have no natural economic boundary.

---

## 7. Economic Governor and Path Selection

Economics is not a reporting dashboard bolted on after the fact. It governs the architecture itself.

```text
AUTHORITATIVE LAYER
What must be true?
        │
        ▼
VERIFICATION CONTRACT
        │
        ▼
ECONOMIC GOVERNOR
What is the cheapest sufficient path
to establish that truth?
        │
        ├── cache?
        ├── deterministic computation?
        ├── smaller model?
        ├── algorithmic verifier?
        ├── agentic verifier?
        ├── stronger model?
        └── human escalation?
        │
        ▼
EXECUTION + VERIFICATION
        │
        ▼
SUFFICIENT EVIDENCE?
        │
     yes│     no
        ▼       │
     ACCEPT     └── economically justified escalation
```

### Model-routing principle

Use the **cheapest sufficient source of competence**:

```text
Exact cache hit                    → use cached verified result
Deterministic program can answer   → do not call a model
Small model is qualified           → use small model
Larger model required              → escalate
Deterministic verification enough  → stop
Semantic uncertainty remains       → invoke agentic verifier
High-impact unresolved uncertainty → escalate model / human
```

Not:

```text
Frontier model → frontier reviewer → frontier critic → frontier judge
```

for every task. That is brute-force inference spending, not harness engineering economics.

### Risk-triggered verification

Expensive intelligence is invoked only when cheaper evidence cannot establish the required property:

```text
                CHANGE
                   │
                   ▼
           Deterministic checks
          cheap / fast / reliable
                   │
                   ▼
             Risk assessment
                   │
          ┌────────┴────────┐
          │                 │
      sufficient        unresolved
       evidence            risk
          │                 │
          ▼                 ▼
        ACCEPT       Agentic verification
                            │
                      ┌─────┴─────┐
                      │           │
                  resolved    unresolved
                      │           │
                      ▼           ▼
                    ACCEPT     escalate /
                               reject
```

---

## 8. Relationship to the Other Layers

| Layer | Fundamental question | Goal |
|-------|----------------------|------|
| **Authoritative** | What must be true? | Define correctness, constraints, permissions, and acceptance |
| **Verifier** | How do we know it is true? | Produce sufficient repository-aware evidence |
| **Economics** | What is the least costly sufficient way to establish and sustain it? | Optimize total cost of correctness under mandatory floors |

**Authority defines truth.  
Verification establishes truth.  
Economics determines the minimum sufficient cost of establishing truth.**

---

## 9. Definition of Done for the Economics Layer

The economics layer is complete when the harness can:

1. Express mandatory floors (correctness, failure containment, safety, authority, verification coverage) as hard constraints.
2. Measure Total Cost of Correctness across all eight cost components.
3. Admit new controls only under the Minimum Sufficient Harness Principle.
4. Select, at runtime, the cheapest sufficient path for each task (cache → deterministic → smaller model → larger model → human).
5. Apply a rational stopping rule once the authoritative evidence threshold is satisfied.
6. Refuse to trade mandatory safety or authority constraints for marginal economic improvement.

---

## 10. Change Control

Changes to this document require:

- Explicit version update
- Confirmation that mandatory floors remain non-negotiable constraints
- Confirmation that the Minimum Sufficient Harness Principle is preserved
- Alignment with AGENTS.md and VERIFICATION.md
