"""S5-2: HTTP provider proposals applied; ACCEPT still from ledger/CI only."""
from pathlib import Path
import json
from specialized_harness.engine.models import FinalStatus
from specialized_harness.engine.loader import load_blueprint
from specialized_harness.engine.blueprint_engine import BlueprintEngine
from specialized_harness.nodes.registry import make_fixture_handlers
from specialized_harness.observability.ledger import EvidenceLedger
from specialized_harness.providers.http import HttpAgentProvider
from specialized_harness.sandboxes.workspace import WorkspaceSandbox

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / "blueprints" / "standard-coding.yaml"
FIX = ROOT / "fixtures"

_FIX_APP = """def add(a, b):
    return a + b
"""


def test_http_provider_can_drive_accept_via_real_ci():
    def opener(req, timeout=30):
        body = json.loads(req.data.decode())
        if body["node_id"] == "implement":
            return json.dumps(
                {
                    "plan_summary": "http implement",
                    "mutations": [
                        {"path": "app.py", "content": _FIX_APP},
                        {"path": "harness_impl_marker.txt", "content": "http\n"},
                    ],
                }
            ).encode()
        return json.dumps({"plan_summary": "noop", "mutations": []}).encode()

    bp = load_blueprint(BP)
    sandbox = WorkspaceSandbox(FIX / "fix_add", "http-accept-1")
    handlers = make_fixture_handlers(FIX, "fix_add")
    ctx = {
        "task": "fix_add",
        "sandbox": sandbox,
        "evidence": {},
        "ledger": EvidenceLedger(),
        "provider": HttpAgentProvider("http://mock.test/p", opener=opener),
    }
    try:
        result = BlueprintEngine(bp, handlers, run_id="http-accept-1", context=ctx).run()
    finally:
        sandbox.teardown()
    assert result.final_status == FinalStatus.ACCEPT
