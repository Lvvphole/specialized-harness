# Agent Engineering Standard (integration)

**Authority**: [AGENTS.md](../AGENTS.md) — the harness remains the only acceptance authority.

## Role

The vendored `.agent-standard/` + `specialized_harness.agent_standard` package supply
**candidate-construction guidance** only (profile + optional language rule text).

They do **not**:

- declare ACCEPT / HUMAN_HANDOFF / FAILED
- expand verifier vocabulary
- execute tools or write the workspace
- merge to main

## Runtime path

```text
run_fixture_task(..., profile=, language=)
        ↓
attach_standard_to_context  →  agent_standard_text in context
        ↓
AgentProvider.propose  (HTTP body includes agent_standard_context)
        ↓
harness apply_proposal → verify → decide
```

CLI:

```bash
specialized-harness run fix_add --profile bug-fix --language python
specialized-harness run --repo /path/to/repo --task "…" --profile general
```

Missing `.agent-standard` is non-fatal for fixture runs (`required=False`).
Unknown profile/language raises configuration error when a standard is loaded.

## Governing context id

Static config fingerprint (example): `aes-v1.0.0-rules33` — not a per-run hash.
