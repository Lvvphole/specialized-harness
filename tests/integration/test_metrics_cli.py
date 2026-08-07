"""S5-1: metrics CLI over real fixture runs."""
from pathlib import Path

from specialized_harness.cli import main
from specialized_harness.runner import run_fixture_task

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / "blueprints" / "standard-coding.yaml"
FIX = ROOT / "fixtures"


def test_metrics_cli_json(tmp_path: Path, capsys):
    run_fixture_task(BP, FIX, "fix_add", run_id="m-accept", runs_dir=tmp_path)
    run_fixture_task(BP, FIX, "always_fail_ci", run_id="m-handoff", runs_dir=tmp_path)
    code = main(["metrics", "--runs-dir", str(tmp_path), "--json"])
    assert code == 0
    out = capsys.readouterr().out
    assert '"runs": 2' in out or '"runs":2' in out.replace(" ", "")
    assert "accept" in out
