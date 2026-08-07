"""Public handler map keys for blueprint + engine aliases."""
from pathlib import Path

from specialized_harness.nodes.registry import make_fixture_handlers

REQUIRED = {
    "resolve_authority",
    "constrain_scope",
    "provision_sandbox",
    "plan",
    "implement",
    "run_local_verification",
    "git_push",
    "selective_ci_and_verify_outcome",
    "selective_ci",
    "fix_ci_failures",
    "decide_accept_or_handoff",
}


def test_handler_map_keys():
    m = make_fixture_handlers(Path("/tmp"), "fix_add")
    assert REQUIRED.issubset(set(m.keys()))
