"""
Clinical Calibration Curve (C³)

Extension of standard ML calibration analysis, stratified by
specialty, disease severity, and demographic group.

Identifies specific confidence-accuracy gaps by clinical context —
a model may be well-calibrated in general medicine but overconfident
in pediatric rare diseases.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import statistics


@dataclass
class CalibrationBin:
    confidence_low: float
    confidence_high: float
    predicted_confidence: float     # Mean confidence in this bin
    actual_accuracy: float          # Observed accuracy in this bin
    sample_count: int
    specialty: Optional[str] = None
    severity: Optional[str] = None  # "mild" | "moderate" | "severe" | "critical"
    demographic_group: Optional[str] = None


class ClinicalCalibrationCurve:
    """
    C³ computes Expected Calibration Error (ECE) stratified by clinical context.

    ECE = Σ (|B_m| / n) × |acc(B_m) - conf(B_m)|

    C³ extends this to compute ECE per: specialty, severity level, demographic group.
    The resulting multi-dimensional calibration profile reveals where a model is
    over- or under-confident in specific clinical contexts.
    """

    def compute(self, bins: List[CalibrationBin]) -> dict:
        total_samples = sum(b.sample_count for b in bins)
        if total_samples == 0:
            raise ValueError("No calibration samples provided")

        ece = self._compute_ece(bins, total_samples)
        overconfident_bins = [
            b for b in bins if b.predicted_confidence > b.actual_accuracy + 0.1
        ]
        underconfident_bins = [
            b for b in bins if b.actual_accuracy > b.predicted_confidence + 0.1
        ]

        specialty_ece = self._stratified_ece(bins, "specialty", total_samples)
        severity_ece = self._stratified_ece(bins, "severity", total_samples)
        demographic_ece = self._stratified_ece(bins, "demographic_group", total_samples)

        return {
            "ece": round(ece, 4),
            "calibration_grade": self._grade(ece),
            "overconfident_bin_count": len(overconfident_bins),
            "underconfident_bin_count": len(underconfident_bins),
            "specialty_ece": specialty_ece,
            "severity_ece": severity_ece,
            "demographic_ece": demographic_ece,
            "total_samples": total_samples,
        }

    def _compute_ece(self, bins: List[CalibrationBin], total: int) -> float:
        return sum(
            (b.sample_count / total) * abs(b.actual_accuracy - b.predicted_confidence)
            for b in bins
        )

    def _stratified_ece(self, bins: List[CalibrationBin], attr: str, total: int) -> Dict[str, float]:
        groups: Dict[str, List[CalibrationBin]] = {}
        for b in bins:
            key = getattr(b, attr) or "unknown"
            groups.setdefault(key, []).append(b)

        return {
            group: round(self._compute_ece(group_bins, total), 4)
            for group, group_bins in groups.items()
        }

    def _grade(self, ece: float) -> str:
        if ece <= 0.02:
            return "Excellent"
        elif ece <= 0.05:
            return "Good"
        elif ece <= 0.10:
            return "Acceptable"
        elif ece <= 0.15:
            return "Poor"
        return "Failing"
