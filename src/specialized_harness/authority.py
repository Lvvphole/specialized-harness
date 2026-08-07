"""Resolve authoritative task sources (AGENTS.md question 1).

Fixture mode (default): ``<root>/<task>/`` must exist.
Repo mode (opt-in): ``<root>/`` is the authority root; task is a brief string
and/or ``TASK.md`` under the root. Missing authority blocks — the model must
not invent requirements.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ResolvedAuthority:
    mode: str  # "fixture" | "repo" | "unknown"
    root: Path
    sources: list[str] = field(default_factory=list)
    brief: str | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None


def resolve_task_authority(
    root: str | Path,
    task: str,
    *,
    task_brief: str | None = None,
    allow_repo_mode: bool = False,
) -> ResolvedAuthority:
    """Establish applicable authority for a run.

    - If ``root/task`` is a directory → fixture mode.
    - Else if ``allow_repo_mode`` and ``root`` is a directory → repo mode
      (requires non-empty brief and/or TASK.md).
    - Else → blocking error.
    """
    base = Path(root)
    task_name = (task or "").strip()
    brief_in = task_brief if task_brief is not None else task_name
    brief = (brief_in or "").strip() or None

    if task_name:
        fixture_path = base / task_name
        if fixture_path.is_dir():
            resolved = fixture_path.resolve()
            return ResolvedAuthority(
                mode="fixture",
                root=resolved,
                sources=["fixture", str(resolved)],
                brief=None,
            )

    if allow_repo_mode and base.is_dir():
        resolved = base.resolve()
        sources = ["repo", str(resolved)]
        task_md = base / "TASK.md"
        brief_text = brief
        if task_md.is_file():
            sources.append(str(task_md.resolve()))
            if not brief_text:
                brief_text = task_md.read_text(encoding="utf-8")[:4000].strip() or None
        if not brief_text:
            return ResolvedAuthority(
                mode="repo",
                root=resolved,
                sources=sources,
                brief=None,
                error=(
                    "Missing task brief: provide a non-empty --task string "
                    "or a TASK.md under the repo root"
                ),
            )
        sources.append("task_brief")
        return ResolvedAuthority(
            mode="repo",
            root=resolved,
            sources=sources,
            brief=brief_text,
        )

    if task_name:
        return ResolvedAuthority(
            mode="unknown",
            root=base,
            sources=[],
            error=f"Unknown fixture task: {task_name}",
        )
    return ResolvedAuthority(
        mode="unknown",
        root=base,
        sources=[],
        error=f"Unknown authority path: {base}",
    )
