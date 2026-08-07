"""Net LOC measurement from workspace diffs (CONSTRAINTS.md max_net_loc)."""
from __future__ import annotations

from collections import Counter
from pathlib import Path


IGNORE_NAMES = {"__pycache__", ".git", ".pytest_cache", ".ruff_cache"}
IGNORE_SUFFIXES = {".pyc"}


def _should_skip(path: Path, root: Path) -> bool:
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        return True
    if any(p in IGNORE_NAMES for p in rel_parts):
        return True
    if path.suffix in IGNORE_SUFFIXES:
        return True
    return not path.is_file()


def snapshot_text_files(root: Path) -> dict[str, str]:
    """Relative path -> file text for text-ish files under root."""
    out: dict[str, str] = {}
    if not root.is_dir():
        return out
    for path in sorted(root.rglob("*")):
        if _should_skip(path, root):
            continue
        try:
            out[str(path.relative_to(root))] = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
    return out


def _line_diff_count(before: str, after: str) -> int:
    """Count added + removed lines via multiset difference."""
    cb, ca = Counter(before.splitlines()), Counter(after.splitlines())
    removed = sum((cb - ca).values())
    added = sum((ca - cb).values())
    return added + removed


def measure_net_loc(baseline: dict[str, str], workspace: Path) -> int:
    """Net LOC = sum over files of (added + removed lines) vs baseline snapshot."""
    current = snapshot_text_files(workspace)
    total = 0
    for key in set(baseline) | set(current):
        before = baseline.get(key, "")
        after = current.get(key, "")
        if before == after:
            continue
        total += _line_diff_count(before, after)
    return total
