"""Local git operations inside the workspace (no implied remote success)."""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GitResult:
    ok: bool
    command: str
    stdout: str
    stderr: str
    exit_code: int


def _run(cwd: Path, args: list[str], timeout_s: int = 30) -> GitResult:
    cmd = ["git", *args]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
        return GitResult(
            ok=proc.returncode == 0,
            command=" ".join(cmd),
            stdout=(proc.stdout or "")[:2000],
            stderr=(proc.stderr or "")[:2000],
            exit_code=proc.returncode,
        )
    except subprocess.TimeoutExpired:
        return GitResult(
            ok=False, command=" ".join(cmd), stdout="", stderr="timeout", exit_code=-1
        )
    except FileNotFoundError:
        return GitResult(
            ok=False, command=" ".join(cmd), stdout="", stderr="git not found", exit_code=-1
        )


def ensure_repo(workspace: Path) -> GitResult:
    git_dir = workspace / ".git"
    if git_dir.exists():
        return GitResult(
            ok=True, command="git status", stdout="already a repo", stderr="", exit_code=0
        )
    r = _run(workspace, ["init"])
    if not r.ok:
        return r
    _run(workspace, ["config", "user.email", "harness@local"])
    _run(workspace, ["config", "user.name", "specialized-harness"])
    return r


def commit_all(workspace: Path, message: str) -> GitResult:
    _run(workspace, ["add", "-A"])
    return _run(workspace, ["commit", "--allow-empty", "-m", message])


def create_branch(workspace: Path, branch: str) -> GitResult:
    return _run(workspace, ["checkout", "-B", branch])
