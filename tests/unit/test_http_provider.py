"""S5-2: HttpAgentProvider protocol + mocked HTTP; env default is Scripted."""
import json

from specialized_harness.providers.base import AgentProposal, AgentProvider
from specialized_harness.providers.http import HttpAgentProvider, provider_from_env
from specialized_harness.providers.scripted import ScriptedProvider


def test_http_provider_protocol():
    def opener(req, timeout=30):
        return json.dumps(
            {
                "plan_summary": "mock plan",
                "mutations": [{"path": "app.py", "content": "x = 1\n"}],
            }
        ).encode()

    p = HttpAgentProvider("http://example.test/propose", opener=opener)
    assert isinstance(p, AgentProvider)
    prop = p.propose("implement", {"task": "fix_add", "run_id": "r1"})
    assert isinstance(prop, AgentProposal)
    assert prop.error is None
    assert prop.plan_summary == "mock plan"
    assert len(prop.mutations) == 1
    assert prop.mutations[0].path == "app.py"


def test_http_provider_error_on_bad_response():
    def opener(req, timeout=30):
        raise TimeoutError("slow")

    p = HttpAgentProvider("http://example.test/propose", opener=opener)
    prop = p.propose("implement", {"task": "t"})
    assert prop.error is not None
    assert "failed" in prop.error


def test_provider_from_env_default_scripted():
    p = provider_from_env(env={})
    assert isinstance(p, ScriptedProvider)


def test_provider_from_env_http_when_url_set():
    p = provider_from_env(env={"HARNESS_PROVIDER_URL": "http://example.test/p"})
    assert isinstance(p, HttpAgentProvider)
    assert p.endpoint == "http://example.test/p"
