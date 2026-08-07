"""Read-only repository inspection inside the sandbox (AGENTS.md Q2).

Providers may call these tools to ground proposals. They cannot write,
escape the workspace, run shell, or declare success.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from specialized_harness.sandboxes.workspace import WorkspaceError, WorkspaceSandbox

MAX_READ_BYTES = 100_000
MAX_LIST_ENTRIES = 500
MAX_SEARCH_HITS = 50
MAX_SEARCH_FILE_BYTES = 200_000


@dataclass
class ToolObservation:
    tool: str
    args: dict[str, Any]
    ok: bool
    detail: str


@dataclass
class RepoInspect:
    """Harness-governed list_dir / read_file / search_code."""

    sandbox: WorkspaceSandbox
    log: list[ToolObservation] = field(default_factory=list)

    def list_dir(self, rel: str = ".") -> list[str]:
        args = {"path": rel}
        try:
            path = self.sandbox.resolve(rel)
            if not path.exists():
                self._rec("list_dir", args, False, "not found")
                raise WorkspaceError(f"list_dir: not found: {rel}")
            if not path.is_dir():
                self._rec("list_dir", args, False, "not a directory")
                raise WorkspaceError(f"list_dir: not a directory: {rel}")
            names = sorted(p.name for p in path.iterdir())[:MAX_LIST_ENTRIES]
            self._rec("list_dir", args, True, f"{len(names)} entries")
            return names
        except WorkspaceError:
            raise
        except OSError as e:
            self._rec("list_dir", args, False, str(e))
            raise WorkspaceError(str(e)) from e

    def read_file(self, rel: str) -> str:
        args = {"path": rel}
        try:
            path = self.sandbox.resolve(rel)
            if not path.is_file():
                self._rec("read_file", args, False, "not a file")
                raise WorkspaceError(f"read_file: not a file: {rel}")
            data = path.read_bytes()
            if len(data) > MAX_READ_BYTES:
                data = data[:MAX_READ_BYTES]
            text = data.decode("utf-8", errors="replace")
            self._rec("read_file", args, True, f"{len(text)} chars")
            return text
        except WorkspaceError:
            raise
        except OSError as e:
            self._rec("read_file", args, False, str(e))
            raise WorkspaceError(str(e)) from e

    def search_code(self, query: str, rel: str = ".") -> list[dict[str, Any]]:
        args = {"query": query, "path": rel}
        if not query:
            self._rec("search_code", args, False, "empty query")
            return []
        try:
            root = self.sandbox.resolve(rel)
            if not root.exists():
                self._rec("search_code", args, False, "not found")
                raise WorkspaceError(f"search_code: not found: {rel}")
            hits: list[dict[str, Any]] = []
            paths = [root] if root.is_file() else sorted(root.rglob("*"))
            for path in paths:
                if not path.is_file():
                    continue
                if path.name == "__pycache__" or "__pycache__" in path.parts:
                    continue
                try:
                    if path.stat().st_size > MAX_SEARCH_FILE_BYTES:
                        continue
                    text = path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                if query not in text:
                    continue
                for i, line in enumerate(text.splitlines(), 1):
                    if query in line:
                        hits.append(
                            {
                                "path": str(path.relative_to(self.sandbox.root)),  # type: ignore[arg-type]
                                "line": i,
                                "text": line[:200],
                            }
                        )
                        if len(hits) >= MAX_SEARCH_HITS:
                            self._rec(
                                "search_code", args, True, f"{len(hits)} hits (capped)"
                            )
                            return hits
            self._rec("search_code", args, True, f"{len(hits)} hits")
            return hits
        except WorkspaceError:
            raise
        except OSError as e:
            self._rec("search_code", args, False, str(e))
            raise WorkspaceError(str(e)) from e

    def tools_called(self) -> list[str]:
        return [
            f"{o.tool}:{o.args.get('path', o.args.get('query', ''))}" for o in self.log
        ]

    def observations(self) -> list[dict[str, Any]]:
        return [
            {"tool": o.tool, "args": o.args, "ok": o.ok, "detail": o.detail}
            for o in self.log
        ]

    def _rec(self, tool: str, args: dict[str, Any], ok: bool, detail: str) -> None:
        self.log.append(ToolObservation(tool=tool, args=args, ok=ok, detail=detail))
