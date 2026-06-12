from hermes_agent.router_core.classifier import MockClassifier, classify_with_scanner
from hermes_agent.router_core.secret_scan import scan_text
from hermes_agent.router_core.types import Decision, Risk, Sensitivity


def test_classifier_cannot_lower_scanner_secret_label():
    scan = scan_text("token sk-abcdefghijklmnopqrstuvwxyzABCDEF123456")
    classifier = MockClassifier(
        sensitivity=Sensitivity.S0_PUBLIC,
        risk=Risk.R0_TRIVIAL,
        rationale="looks public",
    )

    result = classify_with_scanner(scan, classifier)

    assert result.sensitivity == Sensitivity.S4_SECRET
    assert result.risk == Risk.R0_TRIVIAL
    assert result.clamp_applied is True


def test_classifier_exception_fails_closed_to_local_only():
    scan = scan_text("ordinary text")
    classifier = MockClassifier(raise_error=True)

    result = classify_with_scanner(scan, classifier)

    assert result.decision_override == Decision.REQUIRE_LOCAL_ONLY
    assert result.rationale == "classifier_error"


def test_classifier_timeout_fails_closed_to_local_only():
    scan = scan_text("ordinary text")
    classifier = MockClassifier(simulate_timeout=True)

    result = classify_with_scanner(scan, classifier)

    assert result.decision_override == Decision.REQUIRE_LOCAL_ONLY
    assert result.rationale == "classifier_timeout"
