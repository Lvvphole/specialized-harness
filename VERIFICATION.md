# VERIFICATION.md — Repository-Aware Hybrid Verifier

**Status**: Production Authority  
**Version**: 1.0.0  
**Authority Rank**: Parallel to CONSTRAINTS.md; subordinate only to AGENTS.md  
**Aligned With**: AGENTS.md v1.1.0

---

## 1. Purpose

The verifier layer exists to produce sufficient, reproducible, repository-aware evidence that a proposed change satisfies the authoritative contract and intended architecture. It does so through the minimum sufficient combination of algorithmic and bounded agentic verification, using semantic repository navigation and dynamically resolved project-specific constraints, while making every evaluated claim, method, observation, uncertainty, and verdict traceable.

Passing tests is necessary evidence. It is not equivalent to proving that a change belongs in the architecture.

The verifier answers, for every proposed change:

- What must be true?
- What must remain true?
- What is permitted?
- What evidence is sufficient?
- What remains indeterminate?

---

## 2. Canonical Pipeline

```text
AUTHORITATIVE LAYER
Defines:
  "What must be true?"
  "What must remain true?"
  "What is permitted?"
  "What evidence is sufficient?"
             │
             ▼
      VERIFICATION CONTRACT
             │
             ▼
      CONTEXT RESOLUTION
repo + architecture + semantics + dependencies + ADRs + standards
             │
       ┌─────┴─────┐
       ▼           ▼
 ALGORITHMIC     AGENTIC
 VERIFICATION   VERIFICATION
       │           │
       └─────┬─────┘
             ▼
       EVIDENCE LEDGER
             │
             ▼
 PASS / FAIL / INDETERMINATE
             │
             ▼
      ACCEPTANCE GATE
```

---

## 3. Five Cooperating Components

### 3.1 Project Context Resolver

Occurs **before** verification begins.

The resolver does not ask merely “what files changed?”. It establishes:

- What kind of repository is this?
- What component is being changed?
- What owns this behavior?
- What architectural boundaries apply?
- What dependencies may this component use / must not use?
- Which ADRs govern this area?
- Which interfaces and contracts must remain stable?
- Which coding standards apply?
- Which tests constitute relevant evidence?
- What downstream components can be affected?
- What is the intended architecture?

Context is resolved from the repository (AGENTS.md, ARCHITECTURE.md, ADRs, package manifests, directory structure, ownership boundaries, etc.). It is **not** dumped indiscriminately into a context window.

Example resolved context:

```yaml
verification_context:
  component: recommendation-engine
  architecture:
    layer: domain
    allowed_dependencies: [domain/*, shared/types/*]
    forbidden_dependencies: [infrastructure/*, ui/*]
  governing_adrs: [ADR-002]
  standards: [typescript-strict, no-domain-side-effects]
  protected_invariants: [approvalStatus, verification.permissionGranted, published]
  affected_dependents: [recommendation-service, trajectory-policy, publication-gate]
```

### 3.2 Algorithmic Verifier

Deterministic or highly reproducible machinery. Used for every property that machines can establish more reliably than models.

Covers (non-exhaustive):

- Syntax, compilation, type correctness
- Formatting, lint rules
- Dependency boundaries and import restrictions
- Schema and API contract conformance
- Unit, integration, property, invariant, and regression tests
- Security scanners and dependency vulnerability checks
- Coverage requirements, migration validity
- Generated-artifact consistency and build reproducibility
- Runtime assertions

Example:

```text
CHECK A17
Rule: domain/** cannot import infrastructure/**
Observed: src/domain/recommendation.ts imports src/infrastructure/database.ts
Result: FAIL
Evidence: dependency-boundary rule DEP-004
```

There is no reason to ask a language model whether this violates the architecture. The graph proves it.

### 3.3 Agentic Verifier

Bounded semantic judgment for properties that algorithms cannot cheaply establish.

The agentic verifier operates under an explicit **verification contract**. It does not receive an open-ended “review this code” prompt.

It asks questions such as:

- Does this implementation actually solve the requested problem?
- Does it pass tests while violating the intended design?
- Was the behavior placed in the correct abstraction?
- Does the change duplicate existing functionality?
- Was an architectural boundary bypassed?
- Did it solve only the visible example rather than the underlying requirement?
- Are the tests meaningful or merely constructed to make the patch pass?
- Are important edge cases absent?
- Is a dependency technically permitted but architecturally inappropriate?
- Could this produce a semantic regression not represented in the existing suite?

Example verification contract:

```yaml
verify:
  requirement:
    drafting_may_only_change: [nextBestAction.draft]
  inspect:
    - changed code
    - relevant callers / callees
    - dependency graph
    - applicable ADRs
    - tests
    - protected state
  establish:
    - requirement_satisfied
    - architecture_preserved
    - invariants_preserved
    - tests_are_adequate
    - no_unjustified_scope_expansion
  output:
    verdict: [PASS | FAIL | INDETERMINATE]
    evidence_required: true
    unsupported_assertions_forbidden: true
```

### 3.4 Semantic Navigation

Repository awareness does **not** mean stuffing large volumes of source into the verifier prompt.

The retrieval surface must understand:

- symbol definitions and references
- callers and callees
- inheritance and implementations
- imports and dependency graph
- AST structure
- tests associated with symbols
- interfaces, schemas, configuration
- ADRs and ownership boundaries
- git history where necessary

Navigation is structure-aware and symbol-aware, not undifferentiated long-context search. Better navigation reduces tokens, latency, and cost while improving localization accuracy.

### 3.5 Evidence Reconciliation

Critical rule:

> Agentic judgment may supplement deterministic evidence. It may **not** silently override deterministic contradiction.

Examples:

| Algorithmic | Agentic | Final |
|-------------|---------|-------|
| FAIL (forbidden dependency) | PASS (design looks fine) | **FAIL** |
| PASS (all tests green) | FAIL (violates ADR-002) | **FAIL** |
| PASS | INDETERMINATE (concurrency behavior unestablished) | **INDETERMINATE** |

This prevents false certainty. The three possible terminal verdicts are:

- **PASS** — sufficient evidence that the change satisfies the authoritative contract and intended architecture
- **FAIL** — contradiction with authoritative requirements, invariants, or architecture
- **INDETERMINATE** — available evidence is insufficient to decide; escalation required

---

## 4. Knowledge Authority Ordering

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

- Generic knowledge (SOLID, language idioms, common design patterns, security concepts) may live in the model.
- Project-specific authority (dependency rules, ADRs, coding standards, domain semantics, protected invariants, definition of done) must be externally represented, versioned, resolvable, and dynamically supplied. It must not live primarily in model weights.

A model may not override an explicit project rule because it prefers a different architecture.

---

## 5. Four Required Properties

### Intentional
Every verification control exists because it establishes a particular property.

```text
Requirement R7 → Property P12 must hold → Verifier V4 provides evidence for P12
```

Verification is traceable to requirements, not a pile of checks.

### Multilayered

```text
            VERIFICATION
       ┌──────────┼──────────┐
       ▼          ▼          ▼
   Structural  Behavioral  Semantic
   AST/schema  tests       agent review
   imports     runtime     architecture
   deps        properties  intent
```

Different failure classes require different mechanisms.

### Consistent
Identical verification contracts produce the same standard of proof regardless of which coding model generated the change.

```text
GPT-generated patch ─────┐
Claude-generated patch ──┼→ same verifier contract
Gemini-generated patch ──┘
```

The generator does not determine the standard of proof.

### Transparent
Every verdict is inspectable:

```yaml
claim:
  id: INV-07
  statement: "drafting cannot alter publication authority"
method:
  type: deterministic
  verifier: invariant-test
evidence:
  test: drafting-preserves-publication-state
  expected: unchanged
  observed: unchanged
result: PASS
```

```yaml
claim:
  id: ARCH-03
  statement: "change preserves domain/infrastructure boundary"
method:
  type: agentic
  verifier: architecture-review
context: [ADR-002, dependency graph, changed symbols]
finding:
  no_new_boundary_violation: true
confidence: high
result: PASS
```

---

## 6. Relationship to the Rest of the Harness

The Authoritative Layer and the Verifier Layer are not competing agents. They form a single pipeline:

- The Authoritative Layer defines what must be true, what must remain true, what is permitted, and what evidence is sufficient.
- The Verifier Layer produces the evidence and the verdict.
- The Acceptance Gate acts only on that evidence.

Repository context resolution, semantic navigation, constraint resolution, algorithmic checking, and agentic review are **not** five independent features to accumulate. They are parts of one verification pipeline. Each capability enters only when it closes a specific verification gap.

---

## 7. Definition of Done for the Verifier Layer

Given a proposed repository change and a verification contract, the verifier layer can:

1. Resolve the applicable project context (architecture, constraints, ADRs, standards, relevant tests).
2. Execute the minimum sufficient set of algorithmic checks.
3. Execute bounded agentic verification under an explicit contract when semantic judgment is required.
4. Reconcile evidence without allowing agentic judgment to override deterministic contradiction.
5. Emit a PASS, FAIL, or INDETERMINATE verdict together with a complete, inspectable Evidence Ledger.

---

## 8. Change Control

Changes to this document require:

- Explicit version update
- Confirmation that intentionality, multilayering, consistency, and transparency are preserved
- Alignment with AGENTS.md (especially independent declaration of success and the five questions)
