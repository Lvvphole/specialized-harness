"""Disposable workspace sandbox — isolation boundary for a single run.

AGENTS.md / SECURITY.md: execution occurs in a disposable workspace.
Source fixtures and the harness tree must not be mutated by a run.
"""
from __future__ import annotations

import hashlib
import shutil
import tempfile
from pathlib import Path


class WorkspaceError(Exception):
    """Raised when a path escapes the sandbox or provision fails."""


class WorkspaceSandbox:
    """Copy-on-provision workspace rooted at a unique temp directory."""

    def __init__(self, source: Path, run_id: str):
        self.source = source.resolve()
        self.run_id = run_id
        self.root: Path | None = None
        self._source_fingerprint: dict[str, str] = {}

    def provision(self) -> Path:
        if not self.source.is_dir():
            raise WorkspaceError(f"Source fixture not found: {self.source}")
        self._source_fingerprint = fingerprint_tree(self.source)
        parent = Path(tempfile.mkdtemp(prefix=f"harness-{self.run_id[:8]}-"))
        dest = parent / "workspace"
        shutil.copytree(self.source, dest)
        self.root = dest.resolve()
        return self.root

    def resolve(self, relative: str | Path) -> Path:
        """Resolve a relative path inside the workspace; reject escapes."""
        if self.root is None:
            raise WorkspaceError("Sandbox not provisioned")
        candidate = (self.root / relative).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as e:
            raise WorkspaceError(f"Path escapes workspace: {relative}") from e
        return candidate

    def teardown(self) -> None:
        if self.root is None:
            return
        parent = self.root.parent
        shutil.rmtree(parent, ignore_errors=True)
        self.root = None

    def source_unchanged(self) -> bool:
        """True if the original fixture tree still matches pre-run fingerprint."""
        return fingerprint_tree(self.source) == self._source_fingerprint


def fingerprint_tree(root: Path) -> dict[str, str]:
    """Relative path -> sha256 of file contents (sorted, deterministic)."""
    out: dict[str, str] = {}
    if not root.is_dir():
        return out
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.name == "__pycache__" or "__pycache__" in path.parts:
            continue
        rel = str(path.relative_to(root))
        out[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return out
