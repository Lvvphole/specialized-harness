"""
Unit tests that enforce the hard constraints defined in CONSTRAINTS.md and AGENTS.md.
These tests must pass for any production deployment.
"""

import pytest
from pathlib import Path

AUTHORITY_FILES = [
    "AGENTS.md",
    "ARCHITECTURE.md",
    "CONSTRAINTS.md",
    "BLUEPRINTS.md",
    "OBSERVABILITY.md",
    "SECURITY.md",
]


def test_authority_files_exist():
    root = Path(__file__).resolve().parents[2]
    for name in AUTHORITY_FILES:
        path = root / name
        assert path.exists(), f"Missing authority file: {name}"
        assert path.stat().st_size > 500, f"Authority file appears empty or stub: {name}"


def test_max_ci_rounds_is_two():
    """CONSTRAINTS.md and AGENTS.md both require a hard ceiling of 2 CI rounds."""
    root = Path(__file__).resolve().parents[2]
    constraints = (root / "CONSTRAINTS.md").read_text()
    agents = (root / "AGENTS.md").read_text()
    assert "Maximum CI rounds per run | 2" in constraints or "max_ci_rounds: 2" in constraints
    assert "At most two CI rounds" in agents or "two CI rounds" in agents.lower()


def test_blueprint_declares_max_ci_rounds():
    root = Path(__file__).resolve().parents[2]
    blueprint = (root / "blueprints" / "standard-coding.yaml").read_text()
    assert "max_ci_rounds: 2" in blueprint


def test_no_path_to_third_ci_round_in_standard_blueprint():
    """Static check that the standard-coding blueprint cannot schedule a third CI round."""
    root = Path(__file__).resolve().parents[2]
    blueprint = (root / "blueprints" / "standard-coding.yaml").read_text()
    assert "ci_rounds < max_ci_rounds" in blueprint
    assert "ci_rounds >= max_ci_rounds" in blueprint


def test_deterministic_nodes_are_declared():
    root = Path(__file__).resolve().parents[2]
    blueprint = (root / "blueprints" / "standard-coding.yaml").read_text()
    required = ["provision", "hydrate", "local_lint", "push", "ci_round", "finalize"]
    for node in required:
        assert f"id: {node}" in blueprint
