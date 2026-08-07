"""CLI v1: config load, summary, short run resolution."""
from pathlib import Path

import pytest

from specialized_harness.cli import main
from specialized_harness.cli_summary import format_run_summary
from specialized_harness.config import load_config
from specialized_harness.engine.models import FinalStatus, RunResult
from specialized_harness.providers.http import resolve_provider
from specialized_harness.providers.scripted import ScriptedProvider


def test_load_config_missing_returns_defaults(tmp_path: Path):
    cfg = load_config(cwd=tmp_path)
    assert cfg.provider == "scripted"
    assert cfg.blueprint is None


def test_load_config_yaml(tmp_path: Path):
    p = tmp_path / ".specialized-harness.yaml"
    p.write_text(
        "blueprint: blueprints/standard-coding.yaml\n"
        "fixture_root: fixtures\n"
        "provider: scripted\n"
    )
    cfg = load_config(cwd=tmp_path)
    assert cfg.blueprint.endswith("standard-coding.yaml")
    assert cfg.resolved_fixture_root() == "fixtures"


def test_format_run_summary_accept():
    result = RunResult(
        run_id="abc",
        final_status=FinalStatus.ACCEPT,
        trajectory=[],
        total_ms=12,
    )
    text = format_run_summary(
        result,
        task="fix_add",
        provider="scripted",
        claims=[
            {"claim_id": "tests_pass", "verdict": "PASS"},
            {"claim_id": "syntax_clean", "verdict": "PASS"},
        ],
        runs_dir="artifacts/runs",
    )
    assert "ACCEPT" in text
    assert "task=fix_add" in text
    assert "provider=scripted" in text
    assert "PASS" in text and "tests_pass" in text
    assert "artifacts/runs/abc/run.json" in text


def test_resolve_provider_scripted_default():
    p = resolve_provider(provider="scripted")
    assert isinstance(p, ScriptedProvider)


def test_resolve_provider_http_requires_url():
    with pytest.raises(ValueError, match="provider_url"):
        resolve_provider(provider="http")


def test_cli_run_with_config(tmp_path: Path):
    root = Path(__file__).resolve().parents[2]
    code = main(
        [
            "run",
            "fix_add",
            "--blueprint",
            str(root / "blueprints" / "standard-coding.yaml"),
            "--fixture-root",
            str(root / "fixtures"),
            "--runs-dir",
            str(tmp_path / "runs"),
        ]
    )
    assert code == 0
