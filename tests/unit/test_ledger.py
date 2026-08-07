"""Evidence Ledger unit tests."""
from specialized_harness.observability.ledger import EvidenceLedger, Verdict


def test_append_and_mandatory_failures():
    led = EvidenceLedger()
    led.append("syntax_clean", "ws", "py_compile", "ok", Verdict.PASS)
    led.append("tests_pass", "ws", "pytest", "1 failed", Verdict.FAIL)
    fails = led.mandatory_failures()
    assert len(fails) == 1
    assert fails[0].claim_id == "tests_pass"


def test_has_mandatory_pass():
    led = EvidenceLedger()
    led.append("tests_pass", "ws", "pytest", "ok", "PASS")
    assert led.has_mandatory_pass("tests_pass")
    assert not led.has_mandatory_pass("syntax_clean")


def test_to_list_serializable():
    led = EvidenceLedger()
    led.append("a", "s", "m", "o", Verdict.INDETERMINATE, mandatory=False)
    d = led.to_list()[0]
    assert d["verdict"] == "INDETERMINATE"
    assert d["mandatory"] is False
