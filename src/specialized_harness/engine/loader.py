"""Blueprint loader and light schema validation."""
from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml


REQUIRED_TOP = ("apiVersion", "kind", "metadata", "spec")
REQUIRED_SPEC = ("policy", "nodes", "edges")


def load_blueprint(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Blueprint not found: {path}")
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ValueError("Blueprint must be a mapping")
    validate_blueprint(data)
    return data


def validate_blueprint(bp: dict[str, Any]) -> None:
    for k in REQUIRED_TOP:
        if k not in bp:
            raise ValueError(f"Blueprint missing top-level key: {k}")
    spec = bp["spec"]
    for k in REQUIRED_SPEC:
        if k not in spec:
            raise ValueError(f"Blueprint spec missing key: {k}")
    policy = spec["policy"]
    max_ci = int(policy.get("max_ci_rounds", 2))
    if max_ci > 2:
        raise ValueError("Hard constraint: max_ci_rounds cannot exceed 2")
    nodes = spec["nodes"]
    if not nodes:
        raise ValueError("Blueprint contains no nodes")
    ids = [n["id"] for n in nodes]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate node ids in blueprint")
    for edge in spec["edges"]:
        if edge["from"] not in ids or edge["to"] not in ids:
            raise ValueError(f"Edge references unknown node: {edge}")
