"""Engine transition unit tests."""
from pathlib import Path
import pytest
from specialized_harness.engine.loader import load_blueprint, validate_blueprint
from specialized_harness.engine.models import PolicyState
from specialized_harness.policy.enforcer import PolicyEnforcer, PolicyViolation

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / "blueprints" / "standard-coding.yaml"


def test_load_and_validate_blueprint():
    bp = load_blueprint(BP)
    assert bp["metadata"]["name"] == "standard-coding"
    assert bp["spec"]["policy"]["max_ci_rounds"] == 2


def test_reject_max_ci_over_two():
    bp = load_blueprint(BP)
    bp["spec"]["policy"]["max_ci_rounds"] = 3
    with pytest.raises(ValueError, match="max_ci_rounds"):
        validate_blueprint(bp)


def test_third_ci_guard():
    policy = PolicyState(max_ci_rounds=2)
    policy.record_ci_round()
    policy.record_ci_round()
    enf = PolicyEnforcer(policy)
    with pytest.raises(PolicyViolation):
        enf.check_ci_round_allowed()
