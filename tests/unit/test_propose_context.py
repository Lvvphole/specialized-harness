"""S6-1: optional propose context from evidence."""
import json
from specialized_harness.providers.context import build_propose_body
from specialized_harness.providers.http import HttpAgentProvider
from specialized_harness.providers.scripted import ScriptedProvider


def test_build_body_minimal():
    body = build_propose_body("implement", {"task": "fix_add", "run_id": "r1"})
    assert body == {"node_id": "implement", "task": "fix_add", "run_id": "r1"}


def test_build_body_with_evidence():
    body = build_propose_body(
        "fix_ci_failures",
        {
            "task": "t",
            "run_id": "r",
            "evidence": {
                "net_loc": 12,
                "last_ci_ok": False,
                "last_ci_stdout": "FAILED test_x\n",
                "loc_exceeded": False,
            },
        },
    )
    assert body["net_loc"] == 12
    assert body["last_ci_ok"] is False
    assert "FAILED" in body["last_ci_stdout"]
    assert body["loc_exceeded"] is False


def test_http_forwards_context():
    captured = {}

    def opener(req, timeout=30):
        captured["body"] = json.loads(req.data.decode())
        return json.dumps({"plan_summary": "ok", "mutations": []}).encode()

    p = HttpAgentProvider("http://example.test/p", opener=opener)
    p.propose(
        "fix_ci_failures",
        {
            "task": "always_fail_ci",
            "run_id": "r2",
            "evidence": {
                "last_ci_ok": False,
                "last_ci_stdout": "boom",
                "net_loc": 3,
            },
        },
    )
    assert captured["body"]["last_ci_ok"] is False
    assert captured["body"]["last_ci_stdout"] == "boom"
    assert captured["body"]["net_loc"] == 3


def test_scripted_still_works_with_extra_evidence():
    p = ScriptedProvider()
    prop = p.propose(
        "implement",
        {
            "task": "fix_add",
            "run_id": "r",
            "evidence": {"net_loc": 1, "last_ci_ok": False},
        },
    )
    assert prop.error is None
    assert any(m.path == "app.py" for m in prop.mutations)
