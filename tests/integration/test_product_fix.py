"""S3-1: ACCEPT depends on product code repair, not marker alone."""
from pathlib import Path

from specialized_harness.engine.blueprint_engine import BlueprintEngine
from specialized_harness.engine.loader import load_blueprint
from specialized_harness.engine.models import ExitStatus, FinalStatus
from specialized_harness.nodes.deterministic.checks import run_pytest
from specialized_harness.nodes.registry import make_fixture_handlers
from specialized_harness.observability.ledger import EvidenceLedger
from specialized_harness.providers.base import AgentProposal, FileMutation
from specialized_harness.providers.scripted import ScriptedProvider
from specialized_harness.runner import run_fixture_task
from specialized_harness.sandboxes.workspace import WorkspaceSandbox

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / "blueprints" / "standard-coding.yaml"
FIX = ROOT / "fixtures"


def test_fix_add_source_fixture_tests_fail():
    r = run_pytest(FIX / "fix_add")
    assert not r.ok, "fix_add fixture must start broken"


def test_accept_repairs_product_code_in_workspace():
    result = run_fixture_task(BP, FIX, "fix_add", run_id="product-fix-1")
    assert result.final_status == FinalStatus.ACCEPT
    impl = next(e for e in result.trajectory if e.node_id == "implement")
    assert "app.py" in impl.metadata.get("files_changed", [])
    ci = next(e for e in result.trajectory if e.node_id == "ci_round")
    assert ci.exit_status == ExitStatus.SUCCESS
    assert not run_pytest(FIX / "fix_add").ok
    assert "a - b" in (FIX / "fix_add" / "app.py").read_text()


def test_marker_only_provider_cannot_accept():
    class MarkerOnlyProvider:
        def propose(self, node_id, context):
            if node_id == "implement":
                return AgentProposal(
                    mutations=[FileMutation("harness_impl_marker.txt", "marker-only\n")]
                )
            return ScriptedProvider().propose(node_id, context)

    bp = load_blueprint(BP)
    sandbox = WorkspaceSandbox(FIX / "fix_add", "marker-only-1")
    handlers = make_fixture_handlers(FIX, "fix_add")
    ctx = {
        "task": "fix_add",
        "sandbox": sandbox,
        "evidence": {},
        "ledger": EvidenceLedger(),
        "provider": MarkerOnlyProvider(),
    }
    try:
        engine = BlueprintEngine(bp, handlers, run_id="marker-only-1", context=ctx)
        result = engine.run()
    finally:
        sandbox.teardown()
    assert result.final_status != FinalStatus.ACCEPT
