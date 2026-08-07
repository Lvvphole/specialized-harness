# GOAL.md — Ultimate Goal of the Modular Harness

**Status**: Production Authority  
**Version**: 1.0.0  
**Authority Rank**: North-star document; all other authority documents exist in service of this goal  
**Aligned With**: AGENTS.md, CONSTRAINTS.md, VERIFICATION.md, ECONOMICS.md, OBSERVABILITY.md

---

## 1. The Destination

At this point the harness is no longer merely a coding-agent wrapper. It is a **model-agnostic optimization system for discovering, executing, verifying, and economically selecting workflows for complex problem solving**.

**Ultimate goal**

> To make complex AI problem solving an evidence-governed optimization problem rather than a prompt-engineering problem.

**Formal statement**

> The ultimate goal of the modular harness is to discover and execute the minimum-cost workflow that can reliably produce a verifiably correct outcome for a given class of complex problems, while continuously proving through reproducible evaluation, mathematical optimization, and independent evidence that the selected workflow is superior to available alternatives under explicit constraints.

**Short governing statement**

> Find the cheapest sufficient workflow that can reliably solve the problem, prove that it works, and prove why it deserves to replace the alternatives.

**Not a better agent.  
A scientifically governed system for discovering better ways to solve problems.**

### Who optimizes under this goal

The harness serves **engineers/operators** and **vibe coders** alike: people who want reliable, clean, verified outcomes from model-assisted coding without making the model the authority. Workflow search and Cost per Verified Correct Outcome exist so both can get sufficient correctness at minimum sufficient cost — not so a chat UI can declare success.

---

## 2. The Harness Searches a Workflow Space

For any task \(x\) there may be many possible workflows:

\[
W(x) = \{w_1, w_2, \ldots, w_n\}
\]

Examples:

```text
Workflow A   GPT → test → done
Workflow B   small model → deterministic tools → test
Workflow C   frontier model → agentic verifier → CI
Workflow D   small model → failure → frontier escalation → deterministic verifier
Workflow E   repository retrieval → planner → coding model → targeted CI
             → semantic verifier → full regression only if risk-triggered
```

The harness does not declare one architecture universally correct. It determines:

> Which workflow is best for this problem distribution under the required correctness and economic constraints?

That changes the harness from a fixed pipeline into a **workflow optimization engine**.

---

## 3. The Governing Mathematical Problem

Select:

\[
w^* = \arg\min_{w \in W} C(w)
\]

subject to:

\[
\begin{align*}
P(\text{correct} \mid w, x) &\ge \tau_c \\
P(\text{unsafe failure} \mid w, x) &\le \tau_f \\
V(w, x) &\ge \tau_v \\
A(w, x) &= 1
\end{align*}
\]

where:

- \(w\) = candidate workflow  
- \(C(w)\) = total lifecycle execution cost  
- \(P(\text{correct})\) = probability of correct outcome  
- \(P(\text{unsafe failure})\) = failure risk  
- \(V\) = required verification strength  
- \(A\) = satisfaction of mandatory authority constraints  

Of all workflows that satisfy non-negotiable requirements, which one produces the desired outcome most efficiently?

This is stronger than “which model is best?” and stronger than “which prompt is best?”

---

## 4. “Best” Is Multidimensional

A complex workflow cannot be optimized on one variable. Quality is at least:

\[
Q(w) = f(
\text{Correctness},\;
\text{Reliability},\;
\text{Verification},\;
\text{Cost},\;
\text{Latency},\;
\text{FailureContainment},\;
\text{Generalization},\;
\text{Maintainability}
)
\]

The true problem is **constrained multi-objective optimization**. Workflows live on a Pareto frontier:

```text
                        HIGH CORRECTNESS
                              ▲
                              │
                         ●    │
                     ●        │
                  ●           │
               ●              │
            ●                 │
         ●                    │
────────────────────────────────────► LOW COST
```

A workflow is economically interesting when another workflow cannot improve one important dimension without worsening another. Constraints come first; cost optimization operates only among workflows that already satisfy the mandatory floors.

---

## 5. The Proof Requirement

The goal is not to prove absolute global optimality across all possible workflows (often infeasible). The scientifically stronger goal is:

> Produce verifiable mathematical and empirical evidence establishing optimality, bounded optimality, dominance, or Pareto efficiency within a precisely defined workflow search space and set of assumptions.

A defensible claim looks like:

```text
Under:
  • task distribution D
  • models M1–M4
  • tool set T
  • verification policy V
  • latency ceiling 30 s
  • correctness floor 97%
  • cost ceiling $1/task

Workflow W7 has the lowest observed
cost per verified correct outcome.

95% confidence interval: $0.61–$0.68

No evaluated workflow dominates W7
on correctness, cost and latency.

Result reproduced across:
  5 seeds · 3 evaluation runs · 2 repository families
```

This is an evidence-backed engineering claim, not “our agent thinks this workflow is best.”

---

## 6. Evidentiary Optimization

Peer-reviewed methods supply both techniques and standards of evidence:

```text
constrained optimization · Bayesian optimization · multi-armed bandits
contextual bandits · Pareto optimization · sequential decision processes
search algorithms · operations research · statistical hypothesis testing
causal inference · experimental design · reliability engineering
```

Adoption path:

```text
Algorithm
    ↓
mathematical assumptions
    ↓
peer-reviewed / authoritative evidence
    ↓
our implementation
    ↓
our benchmark
    ↓
our observed result
    ↓
statistical confidence
    ↓
production decision
```

The harness does not adopt an algorithm because a blog claims a 40% cost cut. It adopts it when the evidence chain holds.

---

## 7. Two Optimization Loops

### Online optimization (per task)

> What workflow should I run now?

```text
Task
 ↓
classify risk / complexity
 ↓
select qualified workflow
 ↓
execute
 ↓
verify
 ↓
stop or escalate
```

This determines routing.

### Offline optimization (across history)

> Which workflow policies should exist at all?

```text
Traces + evals + correctness + costs + latency + failures
       ↓
workflow experiments
       ↓
statistical evaluation
       ↓
optimization
       ↓
new policy candidate
       ↓
controlled evaluation
       ↓
admit / reject
```

Production experimentation must never redefine authority on the fly. Offline optimization discovers better policies under the same authoritative constraints.

---

## 8. Models Are Replaceable Computational Resources

Model agnosticism is not valuable merely because APIs can be swapped. It enables **competitive allocation of intelligence**.

```text
If Model A does localization best for $0.01 → use it
If deterministic AST navigation does it for $0.0001 → do not use a model
If Model B does architectural reasoning better → invoke it only there
If Model C is required for the hardest 4% of tasks → escalate only those
If a compiler can establish a property exactly → never pay a model to speculate
```

The harness owns:

```text
authority
workflow
evidence
verification
economics
optimization
```

The model does not. GPT, Claude, Gemini, Grok, open-source models, compilers, solvers, databases, search, static analyzers, and human reviewers are all **replaceable computational resources available to the architecture**.

---

## 9. Mature Economic Metrics

Primary engineering measure (for comparable task classes):

\[
\boxed{
\text{Cost per Verified Correct Outcome}
=
\frac{\text{Total Resources Required}}{\text{Verified Correct Outcomes}}
}
\]

Evaluated alongside:

```text
correct-outcome rate
failure-containment rate
verification false-accept rate
latency
human intervention
generalization
```

No single metric may conceal catastrophic weakness in another.

A broader value formulation (when problem value can be expressed):

\[
\boxed{
\text{Verified Solution Efficiency}
=
\frac{\text{Value of Correctly Solved Problems}}{\text{Total Resources Required to Produce Verified Solutions}}
}
\]

with mandatory correctness and safety constraints outside the tradeable denominator.

---

## 10. How the Layers Serve the Goal

```text
                    COMPLEX PROBLEM
                          │
                          ▼
                  AUTHORITATIVE LAYER
              Define required outcome,
             constraints and invariants
                          │
                          ▼
                  WORKFLOW GOVERNOR
          Select candidate problem-solving path
                          │
                          ▼
              MODEL / TOOLS / EXECUTION
                          │
                          ▼
                 VERIFICATION LAYER
                ├ Agentic Loop
                ├ CI Verification Loop
                └ Maintenance Loop
                          │
                          ▼
                  ACCEPTED OUTCOME
                          │
                          ▼
                 OBSERVABILITY LAYER
            Capture trajectory + evidence
                          │
                          ▼
                    EVALUATION
        correctness / reliability / economics
                          │
                          ▼
                 OPTIMIZATION ENGINE
      compare workflows / find Pareto improvements
                          │
                          ▼
                  ECONOMIC GOVERNOR
           Does the improvement earn admission?
                          │
                          ▼
                    ADAPT POLICY
                          │
                          └───────────────┐
                                          │
                         next problem ◀───┘
```

This is a **closed-loop engineering system for workflow discovery**, not merely an agent loop.

---

## 11. The Deepest Objective

Today, AI engineering often asks:

> How do we get this model to solve this problem?

The harness must eventually ask:

> What is the most efficient verifiable computational process for solving this class of problems, regardless of which model, algorithm, tool, or combination performs each step?

That is the more important question.

---

## 12. Locked Ultimate Goal

> The ultimate goal of the modular, model-agnostic harness is to discover, validate, and continuously improve economically scalable workflows for solving complex problems, selecting the minimum sufficient combination of models, deterministic algorithms, tools, verification, and human authority required to produce a verifiably correct outcome. Its optimization claims must be supported by reproducible empirical evidence and mathematically defensible methods, so that workflow changes are admitted because they demonstrate measurable superiority under explicit constraints, not because they appear intuitively better.

**Find the cheapest sufficient workflow that can reliably solve the problem, prove that it works, and prove why it deserves to replace the alternatives.**
