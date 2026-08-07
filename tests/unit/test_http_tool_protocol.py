"""HTTP multi-round tool protocol: harness executes tools, provider proposes only."""
from __future__ import annotations

import json
from pathlib import Path

from specialized_harness.engine.blueprint_engine import BlueprintEngine
from specialized_harness.engine.loader import load_blueprint
from specialized_harness.engine.models import FinalStatus, PolicyState
from specialized_harness.nodes.registry import make_fixture_handlers
from specialized_harness.observability.ledger import EvidenceLedger
from specialized_harness.policy.enforcer import PolicyEnforcer, PolicyViolation
from specialized_harness.providers.http import HttpAgentProvider
from specialized_harness.sandboxes.workspace import WorkspaceSandbox
from specialized_harness.tools.repo_inspect import RepoInspect

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / "blueprints" / "standard-coding.yaml"
FIX = ROOT / "fixtures"
_FIX_APP = "def add(a, b):\n    return a + b\n"


def test_max_tool_rounds_independent_of_ci():
    policy = PolicyState(max_ci_rounds=2, max_tool_rounds=8)
    assert policy.max_ci_rounds == 2
    assert policy.max_tool_rounds == 8
    PolicyEnforcer(policy).check_tool_rounds_config()
    bad = PolicyState(max_tool_rounds=0)
    try:
        PolicyEnforcer(bad).check_tool_rounds_config()
        assert False, "expected PolicyViolation"
    except PolicyViolation:
        pass


def test_http_single_round_final_unchanged():
    def opener(req, timeout=30):
        return json.dumps(
            {
                "plan_summary": "mock plan",
                "mutations": [{"path": "app.py", "content": "x = 1\n"}],
            }
        ).encode()

    p = HttpAgentProvider("http://example.test/propose", opener=opener)
    prop = p.propose("implement", {"task": "fix_add", "run_id": "r1"})
    assert prop.error is None
    assert prop.plan_summary == "mock plan"
    assert len(prop.mutations) == 1
    assert prop.metadata.get("http_rounds") == 1


def test_http_multi_round_tools_then_mutations():
    rounds_seen = []

    def opener(req, timeout=30):
        body = json.loads(req.data.decode())
        rounds_seen.append(body)
        if body["round"] == 0:
            return json.dumps(
                {
                    "tool_calls": [
                        {
                            "id": "c1",
                            "name": "read_file",
                            "arguments": {"path": "app.py"},
                        }
                    ],
                    "token_usage": {"prompt": 10, "completion": 2},
                }
            ).encode()
        assert body["round"] == 1
        assert body["observations"]
        assert body["observations"][0]["ok"] is True
        assert "a - b" in str(body["observations"][0].get("result", ""))
        return json.dumps(
            {
                "plan_summary": "fixed after read",
                "mutations": [
                    {"path": "app.py", "content": _FIX_APP},
                    {"path": "harness_impl_marker.txt", "content": "t\n"},
                ],
                "token_usage": {"prompt": 20, "completion": 5},
            }
        ).encode()

    src = FIX / "fix_add"
    sandbox = WorkspaceSandbox(src, "tool-round")
    sandbox.provision()
    inspect = RepoInspect(sandbox=sandbox)
    try:
        p = HttpAgentProvider("http://example.test/propose", opener=opener)
        prop = p.propose(
            "implement",
            {
                "task": "fix_add",
                "run_id": "r-tools",
                "repo_inspect": inspect,
                "policy": PolicyState(max_tool_rounds=8),
            },
        )
        assert prop.error is None
        assert prop.plan_summary == "fixed after read"
        assert any(m.path == "app.py" for m in prop.mutations)
        assert prop.metadata["http_rounds"] == 2
        assert prop.metadata["token_usage"]["prompt"] == 30
        assert prop.metadata["token_usage"]["completion"] == 7
        assert "read_file" in prop.metadata.get("tools_called", [])
        assert prop.metadata.get("total_http_ms") is not None
    finally:
        sandbox.teardown()
    assert rounds_seen[0]["allowed_tools"] == ["list_dir", "read_file", "search_code"]
    assert rounds_seen[0]["max_tool_rounds"] == 8


def test_http_disallowed_tool_observation():
    def opener(req, timeout=30):
        body = json.loads(req.data.decode())
        if body["round"] == 0:
            return json.dumps(
                {
                    "tool_calls": [
                        {"id": "x", "name": "shell", "arguments": {"cmd": "ls"}}
                    ]
                }
            ).encode()
        obs = body["observations"][0]
        assert obs["ok"] is False
        assert "not allowed" in obs["error"]
        return json.dumps({"plan_summary": "ok", "mutations": []}).encode()

    p = HttpAgentProvider(
        "http://example.test/p", opener=opener, max_tool_rounds=4
    )
    prop = p.propose("implement", {"task": "t", "run_id": "r"})
    assert prop.error is None
    assert prop.metadata["http_rounds"] == 2


def test_http_max_tool_rounds_enforced():
    def opener(req, timeout=30):
        return json.dumps(
            {
                "tool_calls": [
                    {"id": "c", "name": "list_dir", "arguments": {"path": "."}}
                ],
                "token_usage": {"prompt": 1},
            }
        ).encode()

    src = FIX / "fix_add"
    sandbox = WorkspaceSandbox(src, "max-tools")
    sandbox.provision()
    inspect = RepoInspect(sandbox=sandbox)
    try:
        p = HttpAgentProvider(
            "http://example.test/p", opener=opener, max_tool_rounds=2
        )
        prop = p.propose(
            "implement",
            {"task": "t", "run_id": "r", "repo_inspect": inspect},
        )
        assert prop.error is not None
        assert "max_tool_rounds" in prop.error
        assert prop.metadata.get("http_rounds") == 2
        assert prop.metadata.get("token_usage", {}).get("prompt") == 2
    finally:
        sandbox.teardown()


def test_http_multi_round_e2e_accept():
    def opener(req, timeout=30):
        body = json.loads(req.data.decode())
        if body["node_id"] != "implement":
            return json.dumps({"plan_summary": "noop", "mutations": []}).encode()
        if body["round"] == 0:
            return json.dumps(
                {
                    "tool_calls": [
                        {
                            "id": "c1",
                            "name": "read_file",
                            "arguments": {"path": "app.py"},
                        }
                    ],
                    "token_usage": {"prompt": 5, "completion": 1},
                }
            ).encode()
        return json.dumps(
            {
                "plan_summary": "fix after read",
                "mutations": [
                    {"path": "app.py", "content": _FIX_APP},
                    {"path": "harness_impl_marker.txt", "content": "t\n"},
                ],
                "token_usage": {"prompt": 8, "completion": 4},
            }
        ).encode()

    bp = load_blueprint(BP)
    sandbox = WorkspaceSandbox(FIX / "fix_add", "http-tools-e2e")
    handlers = make_fixture_handlers(FIX, "fix_add")
    ctx = {
        "task": "fix_add",
        "sandbox": sandbox,
        "evidence": {},
        "ledger": EvidenceLedger(),
        "provider": HttpAgentProvider("http://mock/tools", opener=opener),
    }
    try:
        result = BlueprintEngine(
            bp, handlers, run_id="http-tools-e2e", context=ctx
        ).run()
    finally:
        sandbox.teardown()
    assert result.final_status == FinalStatus.ACCEPT
    impl = next(e for e in result.trajectory if e.node_id == "implement")
    assert impl.token_usage.get("prompt") == 13
    assert impl.token_usage.get("completion") == 5
    assert impl.tools_called
    assert any("read_file" in t for t in impl.tools_called)


def test_policy_max_tool_rounds_from_blueprint():
    bp = load_blueprint(BP)
    assert bp["spec"]["policy"]["max_tool_rounds"] == 8
    assert bp["spec"]["policy"]["max_ci_rounds"] == 2
