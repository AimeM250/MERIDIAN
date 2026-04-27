"""
ClinHall Index (CHI) — Clinical Hallucination Index

Weights hallucinations by clinical danger level rather than treating all errors equally.
First metric to differentiate hallucinations by harm potential in clinical context.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List


class Severity(Enum):
    CRITICAL = "critical"   # Potential for death or serious harm
    HIGH = "high"           # Significant patient harm
    MEDIUM = "medium"       # Suboptimal care path
    LOW = "low"             # Factual error, no direct harm path


SEVERITY_WEIGHTS = {
    Severity.CRITICAL: 10,
    Severity.HIGH: 5,
    Severity.MEDIUM: 2,
    Severity.LOW: 1,
}


@dataclass
class HallucinationEvent:
    text: str
    severity: Severity
    clinical_context: str
    verified: bool = False


class ClinHallIndex:
    """
    CHI = Σ(hallucination_i × severity_weight_i) / total_outputs

    A CHI of 0.0 means no hallucinations detected.
    Red flag threshold: CHI > 0.05 on critical-tier errors triggers automatic SAC disqualification.
    """

    RED_FLAG_CRITICAL_THRESHOLD = 0.05

    def compute(self, events: List[HallucinationEvent], total_outputs: int) -> dict:
        if total_outputs == 0:
            raise ValueError("total_outputs must be greater than zero")

        weighted_sum = sum(
            SEVERITY_WEIGHTS[e.severity] for e in events
        )
        chi = weighted_sum / total_outputs

        critical_events = [e for e in events if e.severity == Severity.CRITICAL]
        critical_chi = sum(SEVERITY_WEIGHTS[e.severity] for e in critical_events) / total_outputs

        return {
            "chi": round(chi, 4),
            "critical_chi": round(critical_chi, 4),
            "red_flag": critical_chi > self.RED_FLAG_CRITICAL_THRESHOLD,
            "total_hallucinations": len(events),
            "by_severity": {
                s.value: len([e for e in events if e.severity == s])
                for s in Severity
            },
        }
