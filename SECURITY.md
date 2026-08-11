# SECURITY.md — Isolation, Permissions & Threat Model

**Status**: Production Authority  
**Version**: 1.1.0

---

## 1. Threat Model Summary

The primary risks this harness is designed to contain:

- Agent attempts to reach production systems or exfiltrate data.
- Agent attempts to disable or bypass quality gates.
- Runaway cost or resource consumption.
- Poisoning of the trajectory or audit trail.
- Accidental or intentional modification of the harness itself during a run.
- An LLM or agent writing directly to `main`, bypassing human review of authority documents or runtime gates.

---

## 2. Isolation Guarantees

- Every run executes inside a freshly provisioned (or pre-warmed and reset) sandbox.
- The sandbox has no route to production networks or credentials.
- Outbound network access is denied by default; any required package mirrors must be explicitly allow-listed and read-only.
- The sandbox is destroyed at the end of the run. No state persists beyond the artifacts intentionally extracted (code changes, trajectory, PR).

---

## 3. Permission Model

| Subject | Permissions |
|---------|-------------|
| Agent inside sandbox | Full local filesystem, process, and package installation rights |
| Agent outside sandbox | None |
| Deterministic nodes | Only the side effects required by their contract (git, lint, CI submission) |
| Blueprint / policy files | Read-only to the agent; writable only by the harness control plane |
| LLM / coding agent on this repo | May open pull requests from feature branches only; **no** write or merge to `main` |
| Human reviewer / owner | Sole authority to merge to `main` |

---

## 4. Tool Surface Restriction

- Each agentic node receives a declared, minimal tool surface.
- Tools that could affect the outside world (network, production APIs, secret stores) are never included in agentic node surfaces.
- Tool results are size-limited before being returned to the model.

---

## 5. Audit & Non-Repudiation

- Every trajectory is content-addressed and immutable once written.
- The blueprint hash is recorded in the trajectory header.
- Human-handoff records and PRs include a reference to the trajectory identifier.

---

## 6. Operational Controls

- Sandbox images are built from a controlled base and scanned.
- Policy Enforcer is the final runtime authority; it cannot be disabled by configuration that the agent can influence.
- Secrets required for CI or PR creation are injected only into deterministic nodes that need them, never into the agent context.

---

## 7. Repository `main`-branch write model

Threat: an LLM or agent **bypasses human review** by writing directly to `main`, poisoning authority documents, policy, or runtime gates.

| Subject | Write to `main` | Open PR | Merge PR |
|---------|-----------------|---------|----------|
| Human reviewer / owner | Only if emergency path is explicitly allowed by owner | Yes | **Yes (sole merge authority)** |
| LLM / coding agent / bot | **Forbidden** | Yes (feature branch only) | **Forbidden** |
| CI | No (status checks only) | N/A | **Forbidden** |

Required platform controls (to be enabled by the human owner):

- Branch protection on `main`: require pull request; require at least one human approval; dismiss stale reviews; no force push; restrict who can push.
- Do not grant models long-lived credentials with `main` push rights.

See AGENTS.md §8 and CONSTRAINTS.md (Repository governance).

## CI workflow hardening (Tier 0)

- Workflow-level `permissions: {}` (deny by default); jobs grant least privilege.
- Third-party actions SHA-pinned; `persist-credentials: false` on checkout (except Codex advisory job, which uses a scoped job token for base-ref fetch only).
- CI never merges to `main` (AGENTS.md §8).
