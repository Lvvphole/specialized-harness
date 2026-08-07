"""Authority file presence and hard-constraint documentation checks."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

AUTHORITY_FILES = [
    "GOAL.md",
    "AGENTS.md",
    "ARCHITECTURE.md",
    "CONSTRAINTS.md",
    "VERIFICATION.md",
    "ECONOMICS.md",
    "OBSERVABILITY.md",
    "BLUEPRINTS.md",
    "SECURITY.md",
]


def test_authority_files_exist():
    for name in AUTHORITY_FILES:
        path = ROOT / name
        assert path.exists(), f"Missing authority file: {name}"
        assert path.stat().st_size > 500, f"Authority file appears empty: {name}"


def test_blueprint_max_ci_rounds():
    text = (ROOT / "blueprints" / "standard-coding.yaml").read_text()
    assert "max_ci_rounds: 2" in text
    assert "resolve_authority" in text
    assert "decide" in text
