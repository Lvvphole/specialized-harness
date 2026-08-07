"""Executable checks run inside the workspace (algorithmic verification)."""
from __future__ import annotations

import py_compile
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CheckResult:
    ok: bool
    command: str
    exit_code: int
    stdout: str
    stderr: str


def _truncate(s: str, limit: int = 4000) -> str:
    if len(s) <= limit:
        return s
    return s[: limit // 2] + "\n...[truncated]...\n" + s[-limit // 2 :]


def syntax_check(workspace: Path) -> CheckResult:
    """Compile all .py files under workspace (no test execution)."""
    failures: list[str] = []
    checked = 0
    for path in sorted(workspace.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        checked += 1
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as e:
            failures.append(str(e))
    ok = checked > 0 and not failures
    msg = "\n".join(failures) if failures else f"compiled {checked} files"
    return CheckResult(ok=ok, command="py_compile", exit_code=0 if ok else 1, stdout=msg, stderr="")


def run_pytest(workspace: Path, timeout_s: int = 60) -> CheckResult:
    """Run pytest in workspace; deterministic executable proof."""
    cmd = [sys.executable, "-m", "pytest", "-q", "--tb=no"]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(workspace),
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
        return CheckResult(
            ok=proc.returncode == 0,
            command=" ".join(cmd),
            exit_code=proc.returncode,
            stdout=_truncate(proc.stdout or ""),
            stderr=_truncate(proc.stderr or ""),
        )
    except subprocess.TimeoutExpired as e:
        out = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        return CheckResult(
            ok=False,
            command=" ".join(cmd),
            exit_code=-1,
            stdout=_truncate(out),
            stderr=f"timeout after {timeout_s}s",
        )
