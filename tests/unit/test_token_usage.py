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
    assert normalize_token_usage(None) == {}
    assert normalize_token_usage({"prompt": 10, "completion": 5}) == {
        "prompt": 10,
        "completion": 5,
    }
    assert normalize_token_usage({"prompt": "bad"}) == {}


def test_http_provider_surfaces_token_usage():
    def opener(req, timeout=30):
        return json.dumps(
            {
                "plan_summary": "x",
                "mutations": [],
                "token_usage": {"prompt": 11, "completion": 7},
            }
        ).encode()

    prop = HttpAgentProvider("http://t", opener=opener).propose("plan", {"task": "t"})
    assert prop.metadata["token_usage"]["prompt"] == 11


def test_trajectory_carries_token_usage_from_http_provider():
    def opener(req, timeout=30):
        body = json.loads(req.data.decode())
        if body["node_id"] == "implement":
            return json.dumps(
                {
                    "plan_summary": "fix",
                    "mutations": [
                        {"path": "app.py", "content": _FIX_APP},
                        {"path": "harness_impl_marker.txt", "content": "t\n"},
                    ],
                    "token_usage": {"prompt": 100, "completion": 50},
                }
            ).encode()
        return json.dumps(
            {"plan_summary": "noop", "mutations": [], "token_usage": {"prompt": 1}}
        ).encode()

    bp = load_blueprint(BP)
    sandbox = WorkspaceSandbox(FIX / "fix_add", "tok-1")
    handlers = make_fixture_handlers(FIX, "fix_add")
    ctx = {
        "task": "fix_add",
        "sandbox": sandbox,
        "evidence": {},
        "ledger": EvidenceLedger(),
        "provider": HttpAgentProvider("http://mock/p", opener=opener),
    }
    try:
        result = BlueprintEngine(bp, handlers, run_id="tok-1", context=ctx).run()
    finally:
        sandbox.teardown()
    assert result.final_status == FinalStatus.ACCEPT
    impl = next(e for e in result.trajectory if e.node_id == "implement")
    assert impl.token_usage.get("prompt") == 100
    assert impl.token_usage.get("completion") == 50


def test_metrics_mean_total_tokens(tmp_path: Path):
    d = tmp_path / "r1"
    d.mkdir()
    (d / "run.json").write_text(
        json.dumps(
            {
                "run_id": "r1",
                "final_status": "ACCEPT",
                "total_ms": 10,
                "trajectory": [
                    {"token_usage": {"prompt": 10, "completion": 5}},
                    {"token_usage": {}},
                ],
                "claims": [],
            }
        )
    )
    s = summarize_runs_dir(tmp_path)
    assert s.mean_total_tokens == 15.0
