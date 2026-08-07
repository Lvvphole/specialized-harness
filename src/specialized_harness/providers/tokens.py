"""Normalize optional token_usage from provider proposals (ECONOMICS scaffolding)."""
from __future__ import annotations

from typing import Any


def normalize_token_usage(raw: Any) -> dict[str, int]:
    """Accept dict of numeric counts; ignore invalid entries. Empty if absent."""
    if not isinstance(raw, dict):
        return {}
    out: dict[str, int] = {}
    for k, v in raw.items():
        try:
            out[str(k)] = int(v)
        except (TypeError, ValueError):
            continue
    return out
