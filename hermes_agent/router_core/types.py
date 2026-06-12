from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Dict, List, Optional


class Sensitivity(IntEnum):
    S0_PUBLIC = 0
    S1_LOW = 1
    S2_INTERNAL = 2
    S3_CONFIDENTIAL = 3
    S4_SECRET = 4


class Risk(IntEnum):
    R0_TRIVIAL = 0
    R1_LOW = 1
    R2_MODERATE = 2
    R3_HIGH = 3
    R4_CRITICAL = 4


class Decision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_REDACTION = "REQUIRE_REDACTION"
    REQUIRE_HUMAN_APPROVAL = "REQUIRE_HUMAN_APPROVAL"
    REQUIRE_LOCAL_ONLY = "REQUIRE_LOCAL_ONLY"


@dataclass(frozen=True)
class ScanFinding:
    type: str
    value: str
    start: int
    end: int
    fingerprint: str


@dataclass(frozen=True)
class ScanResult:
    redacted_text: str
    findings: List[ScanFinding] = field(default_factory=list)
    implied_sensitivity: Sensitivity = Sensitivity.S0_PUBLIC

    @property
    def redaction_count(self) -> int:
        return len(self.findings)


@dataclass(frozen=True)
class ClassifierResult:
    sensitivity: Sensitivity
    risk: Risk
    rationale: str
    clamp_applied: bool = False
    decision_override: Optional[Decision] = None


@dataclass(frozen=True)
class RouteDecision:
    decision: Decision
    sensitivity: Sensitivity
    risk: Risk
    target_provider: str
    reasons: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class RouteExplanation:
    input_hash: str
    sensitivity: Sensitivity
    risk: Risk
    decision: Decision
    target_provider: str
    reasons: List[str]
    redaction_count: int
    clamp_applied: bool
    budget: Dict[str, Any]
    timestamp: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "input_hash": self.input_hash,
            "sensitivity": self.sensitivity.name,
            "risk": self.risk.name,
            "decision": self.decision.name,
            "target_provider": self.target_provider,
            "reasons": list(self.reasons),
            "redaction_count": self.redaction_count,
            "clamp_applied": self.clamp_applied,
            "budget": dict(self.budget),
            "timestamp": self.timestamp,
        }
