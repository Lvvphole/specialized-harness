"""AgentProvider interface tests."""
from pathlib import Path
from specialized_harness.providers.scripted import ScriptedProvider
from specialized_harness.providers.base import AgentProposal, AgentProvider, FileMutation
from specialized_harness.nodes.agentic.apply import apply_proposal
from specialized_harness.sandboxes.workspace import WorkspaceSandbox


def test_scripted_implement_proposal():
    p = ScriptedProvider()
    prop = p.propose("implement", {"task": "fix_add", "run_id": "r1"})
    assert isinstance(prop, AgentProposal)
    assert any(m.path == "harness_impl_marker.txt" for m in prop.mutations)


def test_scripted_over_loc_bulk():
    p = ScriptedProvider()
    prop = p.propose("implement", {"task": "over_loc", "run_id": "r1"})
    assert any(m.path == "bulk_generated.py" for m in prop.mutations)


def test_apply_proposal_writes_workspace(tmp_path: Path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.py").write_text("x\n")
    sb = WorkspaceSandbox(src, "run-p")
    sb.provision()
    prop = AgentProposal(mutations=[FileMutation("b.py", "hello\n")])
    changed = apply_proposal(sb, prop)
    assert "b.py" in changed
    assert (sb.root / "b.py").read_text() == "hello\n"
    assert (src / "b.py").exists() is False
    sb.teardown()


def test_provider_protocol_satisfied():
    assert isinstance(ScriptedProvider(), AgentProvider)
