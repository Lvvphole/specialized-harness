"""S4-2: public handler map keys stable after modularization."""
from pathlib import Path

from specialized_harness.nodes.registry import make_fixture_handlers

REQUIRED = {
    "resolve_authority",
    "constrain_scope",
    "provision_sandbox",
    "hydrate_context",
    "plan",
    "implement",
    "run_local_verification",
    "run_local_linters",
    "git_push",
    "selective_ci_and_verify_outcome",
    "selective_ci",
    "fix_ci_failures",
    "decide_accept_or_handoff",
    "create_pull_request",
}


def test_handler_map_keys(tmp_path: Path):
    (tmp_path / "t").mkdir()
    h = make_fixture_handlers(tmp_path, "t")
    assert REQUIRED.issubset(h.keys())
