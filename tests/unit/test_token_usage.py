"""S6-2: token_usage from provider → trajectory; metrics when present."""
import json
from pathlib import Path

from specialized_harness.engine.blueprint_engine import BlueprintEngine
from specialized_harness.engine.loader import load_blueprint
from specialized_harness.engine.models import FinalStatus
from specialized_harness.nodes.registry import make_fixture_handlers
from specialized_harness.observability.ledger import EvidenceLedger
from specialized_harness.observability.metrics import summarize_runs_dir
from specialized_harness.providers.http import HttpAgentProvider
from specialized_harness.providers.tokens import normalize_token_usage
from specialized_harness.sandboxes.workspace import WorkspaceSandbox

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / "blueprints" / "standard-coding.yaml"
FIX = ROOT / "fixtures"

_FIX_APP = "def add(a, b):\n    return a + b\n"


def test_normalize_token_usage():
    assert normalize_token_usage(None) is None
    assert normalize_token_usage({"prompt_tokens": 1, "completion_tokens": 2}) == {
        "prompt_tokens": 1,
        "completion_tokens": 2,
        "total_tokens": 3,
    }


def test_http_provider_surfaces_token_usage():
    def opener(req, timeout=30):
        return json.dumps(
            {
                "mutations": [{"path": "app.py", "content": _FIX_APP}],
                "token_usage": {"prompt_tokens": 10, "completion_tokens": 20},
            }
        ).encode()

    p = HttpAgentProvider("http://example.test/propose", opener=opener)
    prop = p.propose("implement", {"task": "fix_add", "run_id": "t", "evidence": {}})
    assert prop.error is None
    assert prop.metadata.get("token_usage", {}).get("total_tokens") == 30


def test_trajectory_carries_token_usage_from_http_provider(tmp_path: Path):
    def opener(req, timeout=30):
        return json.dumps(
            {
                "mutations": [{"path": "app.py", "content": _FIX_APP}],
                "token_usage": {"prompt_tokens": 5, "completion_tokens": 7},
            }
        ).encode()

    provider = HttpAgentProvider("http://example.test/propose", opener=opener)
    task = "fix_add"
    source = FIX / task
    rid = "tok-run"
    sandbox = WorkspaceSandbox(source, rid)
    handlers = make_fixture_handlers(FIX, task)
    ctx = {
        "task": task,
        "sandbox": sandbox,
        "fixture_source": source.resolve(),
        "evidence": {},
        "ledger": EvidenceLedger(),
        "provider": provider,
    }
    try:
        bp = load_blueprint(BP)
        result = BlueprintEngine(bp, handlers, run_id=rid, context=ctx).run()
        assert result.final_status == FinalStatus.ACCEPT
        implement_ev = next(e for e in result.trajectory if e.node_id == "implement")
        assert implement_ev.token_usage is not None
        assert implement_ev.token_usage.get("total_tokens") == 12
    finally:
        sandbox.teardown()


def test_metrics_mean_total_tokens(tmp_path: Path):
    runs = tmp_path / "runs"
    (runs / "a").mkdir(parents=True)
    (runs / "a" / "run.json").write_text(
        json.dumps(
            {
                "run_id": "a",
                "final_status": "ACCEPT",
                "trajectory": [
                    {
                        "node_id": "implement",
                        "status": "success",
                        "token_usage": {"total_tokens": 100},
                    }
                ],
                "claims": [],
                "total_ms": 1,
            }
        )
    )
    s = summarize_runs_dir(runs)
    d = s.to_dict()
    assert d.get("mean_total_tokens") == 100.0
