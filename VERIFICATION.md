# VERIFICATION.md — Repository-Aware Hybrid Verifier

**Status**: Production Authority  
**Version**: 1.1.0  
**Authority Rank**: Parallel to CONSTRAINTS.md; subordinate only to AGENTS.md  
**Aligned With**: AGENTS.md v1.1.0

---

## 1. Purpose

The verifier layer exists to produce sufficient, reproducible, repository-aware evidence that a proposed change satisfies the authoritative contract and intended architecture. It does so through the minimum sufficient combination of algorithmic and bounded agentic verification, using semantic repository navigation and dynamically resolved project-specific constraints, while making every evaluated claim, method, observation, uncertainty, and verdict traceable.

Passing tests is necessary evidence. It is not equivalent to proving that a change belongs in the architecture.

The overarching objective of the verifier layer is:

> To establish and preserve sufficient evidence that accepted repository states satisfy authoritative requirements, intended architecture, and protected invariants, using bounded agentic reasoning for semantic uncertainty, deterministic CI for executable proof, and maintenance controls to prevent the repository itself from degrading the reliability of future verification.

---

## 2. Canonical Pipeline

```text
                 AUTHORITATIVE LAYER
                        │
              Verification contract
                        │
                        ▼
                CONTEXT RESOLUTION
                        │
          repo / architecture / semantics
                        │
             ┌──────────┴──────────┐
             │                     │
             ▼                     ▼
      AGENTIC LOOP           CI VERIFY LOOP
semantic / architectural     executable proof
reasoning                    and regression
             │                     │
             └──────────┬──────────┘
                        ▼
                EVIDENCE LEDGER
                        │
            PASS / FAIL / INDETERMINATE
                        │
                        ▼
                 ACCEPTANCE GATE
                        │
                        ▼
                   REPOSITORY
                        │
                        ▼
              CODE MAINTENANCE LOOP
                        │
              drift / decay / entropy
                        │
                        └──────► back through
                                 verification
```

The three loops solve different verification problems and different time horizons. They must not be collapsed into one generic “review loop.”

| Loop | Primary question | Time horizon |
|------|------------------|--------------|
| **Agentic Verification Loop** | Does this implementation make semantic and architectural sense? | During the change |
| **CI Verification Loop** | Does this candidate satisfy executable requirements? | Before acceptance |
| **Code Maintenance Loop** | Is the repository remaining healthy and verifiable over time? | After and between changes |

---

## 3. The Three Loops

### 3.1 Agentic Verification Loop

**Canonical definition**

> The Agentic Verification Loop exists to resolve semantic, architectural, and intent-level uncertainty through bounded repository-aware reasoning, correction, and re-evaluation until sufficient evidence supports PASS, contradiction establishes FAIL, or unresolved uncertainty requires INDETERMINATE or escalation.

**Goal**

Iteratively inspect, challenge, and refine a proposed change until the verifier has sufficient semantic and architectural confidence that the implementation satisfies the authoritative intent, not merely the visible tests.

It exists because many properties cannot be established cheaply by static checks alone:

- whether the change actually solves the underlying requirement
- whether the implementation belongs in the chosen abstraction
- whether architecture is being bypassed
- whether relevant dependencies, callers, and downstream effects were missed
- whether tests are meaningful or merely shaped around the patch
- whether hidden semantic regressions are plausible
- whether scope expanded unnecessarily
- whether the agent misunderstood the repository’s intended design

**Loop shape**

```text
Proposed change
      ↓
Resolve relevant repository context
      ↓
Inspect changed symbols and affected graph
      ↓
Compare implementation to authoritative intent
      ↓
Identify semantic / architectural gaps
      ↓
Request correction or additional evidence
      ↓
Re-evaluate
      ↓
PASS | FAIL | INDETERMINATE
```

**Hard constraint**

The Agentic Loop is **not** an unlimited self-reflection loop. It terminates when one of three conditions occurs:

```text
Sufficient evidence exists → PASS
Contradiction exists → FAIL
Remaining uncertainty cannot be economically or technically resolved → INDETERMINATE
```

Its purpose is not “keep reviewing until the model feels confident.”  
Its purpose is to close semantic verification gaps that deterministic machinery cannot close.

### 3.2 CI Verification Loop

**Canonical definition**

> The CI Verification Loop exists to establish reproducible machine evidence that the candidate repository state satisfies every applicable executable requirement, invariant, policy, and regression gate, rerunning only the checks necessary to close identified failures until the candidate passes or is rejected.

**Goal**

Repeatedly execute the repository’s authoritative machine-verifiable checks against the actual candidate state until the change either satisfies all required executable gates or is rejected.

Responsible for:

```text
build / compile / typecheck / lint / format validation
unit / integration / contract / schema / invariant / regression tests
dependency-boundary checks / security scans
generated-artifact checks / migration validation
repository policy checks
```

**Loop shape**

```text
Candidate change
      ↓
Run applicable CI verification contract
      ↓
Collect machine evidence
      ↓
Failures?
   ┌──┴───┐
  yes     no
   │       │
   ▼       ▼
diagnose  required executable
failure   evidence satisfied
   │       │
   ▼       ▼
correct   PASS
   │
   └────────→ rerun affected gates
```

**Selective without becoming permissive**

Not every patch needs the entire repository’s most expensive test matrix. The authoritative verification contract determines required checks from:

```text
changed surface
     +
dependency impact
     +
risk classification
     +
mandatory controls
     ↓
required CI checks
```

Examples:

- docs-only → markdown / lint / link validation  
- domain logic → typecheck + unit + invariant + affected integration tests  
- dependency change → above + vulnerability + license + lockfile checks  
- database migration → migration + schema + integration + rollback verification  

The CI loop provides **reproducible executable evidence**, not model opinion.

### 3.3 Code Maintenance Loop

**Canonical definition**

> The Code Maintenance Loop exists to detect and economically remediate architectural drift, dependency decay, verification degradation, technical debt, security exposure, and structural entropy that would otherwise reduce the repository’s maintainability, correctness, or future verifiability.

**Goal**

Continuously preserve the repository’s intended architecture, quality, operability, and verification power as the system evolves, preventing accumulated change from degrading the assumptions that made earlier verification trustworthy.

The Agentic Loop asks: *Is this change semantically correct?*  
The CI Loop asks: *Does this candidate pass the required executable gates?*  
The Maintenance Loop asks: *Is the repository itself still healthy enough for those answers to remain trustworthy over time?*

It deals with decay:

```text
tests become flaky
dependencies become stale
dead code accumulates
architecture boundaries erode
lint exceptions grow
duplicate abstractions appear
verification coverage declines
ADRs become inconsistent with implementation
generated documentation drifts
temporary workarounds become permanent
security vulnerabilities emerge
unused feature flags remain
technical debt increases
```

A repository can reach a state where CI still reports green while the system has become progressively harder to verify. That is what this loop prevents.

**Loop shape**

```text
Repository over time
       ↓
Observe structural / quality / verification signals
       ↓
Detect drift or degradation
       ↓
Classify (architecture / dependency / tests / complexity /
          security / documentation / dead code / verification quality)
       ↓
Determine whether remediation is justified
       ↓
Create bounded maintenance change
       ↓
Agentic + CI verification
       ↓
Repository health restored
```

**Economic governance**

Maintenance actions require evidence of degradation. The loop is not “continuously improve the code.” Uncontrolled aesthetic refactoring is rejected. Examples of justified triggers:

```text
test flakiness > threshold
dependency vulnerability exists
cyclomatic complexity crossed policy threshold
forbidden dependency count increased
duplicate implementation detected
verification runtime exceeded budget
obsolete code path confirmed unreachable
ADR/implementation contradiction detected
```

**Critical rule**

The Maintenance Loop does **not** bypass the other loops. Any maintenance change must pass through the same verification architecture:

```text
Maintenance detects problem
        ↓
Maintenance proposes change
        ↓
Agentic verification
        ↓
CI verification
        ↓
Acceptance
```

Maintenance never receives privileged permission to quietly rewrite the repository.

---

## 4. Relationship Between Agentic and CI Loops

They are **complementary, not sequentially redundant**.

**Bad design**

```text
Agent 1 reviews patch
↓
Agent 2 reviews patch
↓
Agent 3 reviews patch
↓
CI
```

**Correct design**

```text
CI identifies factual failure
        ↓
Agent reasons about root cause
        ↓
Patch corrected
        ↓
CI proves correction
```

or

```text
CI passes
        ↓
Agentic verifier detects architecture violation
        ↓
Correction
        ↓
CI confirms correction did not break behavior
```

**Core design principle**

> Algorithms establish facts. Agents interpret gaps. Algorithms confirm corrections.

---

## 5. Five Cooperating Components (Supporting Machinery)

### 5.1 Project Context Resolver

Occurs before verification begins. Resolves architecture, ownership, boundaries, ADRs, standards, relevant tests, and downstream impact from the repository. Context is not dumped indiscriminately into a context window.

### 5.2 Algorithmic Verifier

Deterministic or highly reproducible machinery for every property machines can establish more reliably than models (syntax, types, lint, dependency boundaries, tests, schemas, security, migrations, etc.).

### 5.3 Agentic Verifier

Bounded semantic judgment under an explicit verification contract. Operates inside the Agentic Verification Loop. Does not receive open-ended “review this code” prompts.

### 5.4 Semantic Navigation

Structure-aware and symbol-aware retrieval (definitions, references, callers/callees, dependency graph, associated tests, ADRs). Not undifferentiated long-context search.

### 5.5 Evidence Reconciliation

Critical rule: Agentic judgment may supplement deterministic evidence; it may **not** silently override deterministic contradiction. Terminal verdicts: PASS / FAIL / INDETERMINATE.

---

## 6. Knowledge Authority Ordering

```text
AUTHORITATIVE REPO STATE
        >
PROJECT-SPECIFIC RESOLVED CONTEXT
        >
EXECUTABLE OBSERVATIONS
        >
MODEL GENERAL KNOWLEDGE
        >
MODEL OPINION
```

Project-specific authority must be externally represented, versioned, and dynamically supplied. A model may not override an explicit project rule because it prefers a different architecture.

---

## 7. Four Required Properties

- **Intentional** — every control exists because it establishes a particular property (Requirement → Property → Verifier).
- **Multilayered** — structural, behavioral, and semantic verification address different failure classes.
- **Consistent** — identical verification contracts produce the same standard of proof regardless of which model generated the change.
- **Transparent** — every claim, method, observation, uncertainty, and verdict is inspectable in the Evidence Ledger.

---

## 8. Definition of Done for the Verifier Layer

Given a proposed repository change and a verification contract, the verifier layer can:

1. Resolve the applicable project context.
2. Execute the minimum sufficient set of algorithmic checks (CI Verification Loop).
3. Execute bounded agentic verification under an explicit contract when semantic judgment is required (Agentic Verification Loop).
4. Reconcile evidence without allowing agentic judgment to override deterministic contradiction.
5. Emit a PASS, FAIL, or INDETERMINATE verdict together with a complete, inspectable Evidence Ledger.
6. Support ongoing repository health via the Code Maintenance Loop, whose changes themselves pass through the same verification architecture.

---

## 9. Change Control

Changes to this document require:

- Explicit version update
- Confirmation that the three loops remain distinct in purpose and time horizon
- Confirmation that intentionality, multilayering, consistency, and transparency are preserved
- Alignment with AGENTS.md (especially independent declaration of success and the five questions)
