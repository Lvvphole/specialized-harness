"""Apply provider proposals inside the workspace (harness-owned side effects)."""
from __future__ import annotations

from specialized_harness.providers.base import AgentProposal
from specialized_harness.sandboxes.workspace import WorkspaceError, WorkspaceSandbox


def apply_proposal(sandbox: WorkspaceSandbox, proposal: AgentProposal) -> list[str]:
    """Write mutations under sandbox; returns list of relative paths changed."""
    changed: list[str] = []
    if sandbox.root is None:
        raise WorkspaceError("Workspace not provisioned")
    for mut in proposal.mutations:
        path = sandbox.resolve(mut.path)
        if mut.content is None:
            if path.exists():
                path.unlink()
                changed.append(mut.path)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(mut.content)
        changed.append(mut.path)
    return changed
