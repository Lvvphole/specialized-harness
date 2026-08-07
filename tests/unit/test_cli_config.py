"""CLI v1: config load, summary, short run resolution."""
import json
from pathlib import Path

import pytest

from specialized_harness.cli import main
from specialized_harness.cli_summary import format_run_summary
from specialized_harness.config import load_config
from specialized_harness.engine.models import (
    ExitStatus,
    FinalStatus,
    NodeType,
    RunResult,
    TrajectoryEvent,
)
from specialized_harness.providers.http import resolve_provider
from specialized_harness.providers.scripted import ScriptedProvider


def _failed_event(node_id: str, error: str) -> TrajectoryEvent:
    return TrajectoryEvent(
        run_id="abc",
        node_id=node_id,
        node_type=NodeType.DETERMINISTIC,
        sequence=1,
        started_at="2026-01-01T00:00:00+00:00",
        finished_at="2026-01-01T00:00:00+00:00",
        exit_status=ExitStatus.FAILURE,
        ci_round=0,
        recovery_attempt=0,
        token_usage={},
        tools_called=[],
        artifacts=[],
        error=error,
        metadata={},
    )


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


def test_summary_surfaces_node_diagnostic_when_run_error_is_none():
    """A node failure must be visible in the summary, not only in run.json."""
    result = RunResult(
        run_id="abc",
        final_status=FinalStatus.FAILED,
        trajectory=[_failed_event("resolve_authority", "Unknown fixture task: nope")],
        total_ms=0,
    )
    assert result.error is None
    text = format_run_summary(result, task="nope", provider="scripted")
    assert "resolve_authority: Unknown fixture task: nope" in text


def test_summary_prefers_run_level_error_over_node_error():
    result = RunResult(
        run_id="abc",
        final_status=FinalStatus.FAILED,
        trajectory=[_failed_event("push", "node level")],
        error="run level",
        total_ms=0,
    )
    text = format_run_summary(result, task="t", provider="scripted")
    assert "error run level" in text
    assert "node level" not in text


def test_cli_unknown_provider_is_a_clean_error(capsys):
    """Operator typos report one line, not a traceback."""
    root = Path(__file__).resolve().parents[2]
    with pytest.raises(SystemExit) as excinfo:
        main(
            [
                "run",
                "fix_add",
                "--blueprint",
                str(root / "blueprints" / "standard-coding.yaml"),
                "--fixture-root",
                str(root / "fixtures"),
                "--provider",
                "bogus",
            ]
        )
    assert "unknown provider" in str(excinfo.value)


def test_cli_missing_config_file_is_a_clean_error(tmp_path: Path):
    with pytest.raises(SystemExit) as excinfo:
        main(["run", "fix_add", "--config", str(tmp_path / "absent.yaml")])
    assert "config not found" in str(excinfo.value)


def test_metrics_defaults_to_config_runs_dir(tmp_path: Path, monkeypatch, capsys):
    """`metrics` must read where `run` writes, or it reports on an empty dir."""
    runs_dir = tmp_path / "myruns"
    root = Path(__file__).resolve().parents[2]
    (tmp_path / ".specialized-harness.yaml").write_text(
        f"blueprint: {root / 'blueprints' / 'standard-coding.yaml'}\n"
        f"fixture_root: {root / 'fixtures'}\n"
        f"runs_dir: {runs_dir}\n"
    )
    monkeypatch.chdir(tmp_path)

    assert main(["run", "fix_add"]) == 0
    assert list(runs_dir.glob("*/run.json")), "run did not write to config.runs_dir"
    capsys.readouterr()

    assert main(["metrics", "--json"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["runs"] == 1, "metrics read a different directory than run wrote"
    assert summary["accept"] == 1


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
