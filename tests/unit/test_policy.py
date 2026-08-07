"""Policy enforcement unit tests."""
import pytest

from specialized_harness.engine.models import PolicyState
from specialized_harness.policy.enforcer import PolicyEnforcer, PolicyViolation


def test_ci_round_allowed_then_blocked():
    policy = PolicyState(max_ci_rounds=2)
    enf = PolicyEnforcer(policy)
    enf.check_ci_round_allowed()
    policy.record_ci_round()
    enf.check_ci_round_allowed()
    policy.record_ci_round()
    with pytest.raises(PolicyViolation):
        enf.check_ci_round_allowed()


def test_loc_limit():
    policy = PolicyState(max_net_loc=1000)
    enf = PolicyEnforcer(policy)
    enf.check_loc_allowed(1000)
    with pytest.raises(PolicyViolation):
        enf.check_loc_allowed(1001)


def test_trajectory_completeness():
    enf = PolicyEnforcer(PolicyState())
    enf.require_trajectory_complete(5, 5)
    with pytest.raises(PolicyViolation):
        enf.require_trajectory_complete(2, 5)
