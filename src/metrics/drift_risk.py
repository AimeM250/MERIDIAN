"""
Drift Risk Index (DRI)

Predictive longitudinal metric using statistical process control adapted for clinical AI.
Detects deployment performance degradation before it becomes a patient safety event.
"""

from dataclasses import dataclass
from typing import List, Optional
import statistics
import math


@dataclass
class PerformanceSnapshot:
    timestamp: str          # ISO 8601
    meridian_score: float
    chi: float
    egs: float
    specialty: Optional[str] = None
    model_version: Optional[str] = None


class DriftRiskIndex:
    """
    DRI uses statistical process control (SPC) to detect when a deployed
    model's performance is drifting outside acceptable control limits.

    Based on CUSUM (Cumulative Sum Control Chart) adapted for clinical AI.

    DRI interpretation:
      0.0 – 0.3  : Stable — no action needed
      0.3 – 0.6  : Monitor — increase evaluation frequency
      0.6 – 0.8  : Alert — revalidation recommended
      0.8 – 1.0  : Critical — immediate revalidation required
    """

    REVALIDATION_THRESHOLD = 0.6
    CRITICAL_THRESHOLD = 0.8

    def __init__(self, baseline_snapshots: List[PerformanceSnapshot], k: float = 0.5):
        if len(baseline_snapshots) < 5:
            raise ValueError("At least 5 baseline snapshots required to establish control limits")
        self.baseline = baseline_snapshots
        self.k = k  # allowable slack (half the minimum detectable shift)
        self._compute_control_limits()

    def _compute_control_limits(self):
        scores = [s.meridian_score for s in self.baseline]
        self.mu = statistics.mean(scores)
        self.sigma = statistics.stdev(scores)
        self.ucl = self.mu + 3 * self.sigma   # Upper control limit
        self.lcl = self.mu - 3 * self.sigma   # Lower control limit

    def compute(self, recent_snapshots: List[PerformanceSnapshot]) -> dict:
        if not recent_snapshots:
            raise ValueError("At least one recent snapshot required")

        cusum_pos = 0.0
        cusum_neg = 0.0
        cusum_values = []

        for snap in recent_snapshots:
            xi = snap.meridian_score
            cusum_pos = max(0, cusum_pos + (xi - self.mu) / self.sigma - self.k)
            cusum_neg = max(0, cusum_neg - (xi - self.mu) / self.sigma - self.k)
            cusum_values.append(max(cusum_pos, cusum_neg))

        max_cusum = max(cusum_values)
        recent_mean = statistics.mean([s.meridian_score for s in recent_snapshots])
        mean_shift = (self.mu - recent_mean) / self.sigma if self.sigma > 0 else 0

        dri = min(1.0, max(0.0, max_cusum / 10.0))

        return {
            "dri": round(dri, 4),
            "status": self._status(dri),
            "revalidation_required": dri >= self.REVALIDATION_THRESHOLD,
            "critical_alert": dri >= self.CRITICAL_THRESHOLD,
            "baseline_mean": round(self.mu, 4),
            "current_mean": round(recent_mean, 4),
            "mean_shift_sigma": round(mean_shift, 4),
            "control_limits": {"ucl": round(self.ucl, 4), "lcl": round(self.lcl, 4)},
            "snapshots_analyzed": len(recent_snapshots),
        }

    def _status(self, dri: float) -> str:
        if dri < 0.3:
            return "stable"
        elif dri < 0.6:
            return "monitor"
        elif dri < 0.8:
            return "alert"
        return "critical"
