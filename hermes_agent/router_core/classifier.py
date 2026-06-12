from typing import Protocol

from hermes_agent.router_core.types import (
    ClassifierResult,
    Decision,
    Risk,
    ScanResult,
    Sensitivity,
)


class LocalClassifier(Protocol):
    def classify(self, redacted_text: str) -> ClassifierResult:
        ...


class MockClassifier:
    def __init__(
        self,
        sensitivity: Sensitivity = Sensitivity.S0_PUBLIC,
        risk: Risk = Risk.R0_TRIVIAL,
        rationale: str = "mock",
        raise_error: bool = False,
        simulate_timeout: bool = False,
    ) -> None:
        self.sensitivity = sensitivity
        self.risk = risk
        self.rationale = rationale
        self.raise_error = raise_error
        self.simulate_timeout = simulate_timeout

    def classify(self, redacted_text: str) -> ClassifierResult:
        if self.simulate_timeout:
            raise TimeoutError("mock classifier timeout")
        if self.raise_error:
            raise RuntimeError("mock classifier error")
        return ClassifierResult(
            sensitivity=self.sensitivity,
            risk=self.risk,
            rationale=self.rationale,
        )


def classify_with_scanner(
    scan_result: ScanResult,
    classifier: LocalClassifier,
) -> ClassifierResult:
    try:
        advisory = classifier.classify(scan_result.redacted_text)
    except TimeoutError:
        return ClassifierResult(
            sensitivity=Sensitivity.S4_SECRET,
            risk=Risk.R4_CRITICAL,
            rationale="classifier_timeout",
            decision_override=Decision.REQUIRE_LOCAL_ONLY,
        )
    except Exception:
        return ClassifierResult(
            sensitivity=Sensitivity.S4_SECRET,
            risk=Risk.R4_CRITICAL,
            rationale="classifier_error",
            decision_override=Decision.REQUIRE_LOCAL_ONLY,
        )

    final_sensitivity = max(scan_result.implied_sensitivity, advisory.sensitivity)
    return ClassifierResult(
        sensitivity=final_sensitivity,
        risk=advisory.risk,
        rationale=advisory.rationale,
        clamp_applied=final_sensitivity != advisory.sensitivity,
        decision_override=advisory.decision_override,
    )
