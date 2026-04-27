"""
EquityGap Score (EGS)

Intersectional bias detection across demographic attribute combinations.
Goes beyond single-axis equity analysis to measure performance at
intersections of race × age × gender × socioeconomic status.
"""

from dataclasses import dataclass, field
from itertools import combinations
from typing import Dict, List, Optional
import statistics


@dataclass
class DemographicGroup:
    race: Optional[str] = None
    age_bracket: Optional[str] = None   # e.g., "18-34", "65+"
    gender: Optional[str] = None
    ses_bracket: Optional[str] = None   # socioeconomic status bracket

    def label(self) -> str:
        parts = [v for v in [self.race, self.age_bracket, self.gender, self.ses_bracket] if v]
        return " × ".join(parts) if parts else "overall"


@dataclass
class GroupPerformance:
    group: DemographicGroup
    accuracy: float
    calibration_error: float
    sample_size: int
    metrics: Dict[str, float] = field(default_factory=dict)


class EquityGapScore:
    """
    EGS measures the maximum performance disparity across intersectional groups.

    EGS = 1 - (max_group_accuracy - min_group_accuracy)

    A score of 1.0 represents perfect equity. Scores below 0.85 flag significant disparity.
    """

    DISPARITY_FLAG_THRESHOLD = 0.15  # >15% gap flags equity concern

    def compute(self, group_performances: List[GroupPerformance]) -> dict:
        if len(group_performances) < 2:
            raise ValueError("At least two demographic groups required for equity analysis")

        accuracies = [g.accuracy for g in group_performances]
        max_acc = max(accuracies)
        min_acc = min(accuracies)
        disparity = max_acc - min_acc
        egs = round(1 - disparity, 4)

        worst_group = min(group_performances, key=lambda g: g.accuracy)
        best_group = max(group_performances, key=lambda g: g.accuracy)

        calibration_gaps = [g.calibration_error for g in group_performances]

        return {
            "egs": egs,
            "disparity": round(disparity, 4),
            "equity_flag": disparity > self.DISPARITY_FLAG_THRESHOLD,
            "worst_performing_group": worst_group.group.label(),
            "worst_group_accuracy": round(worst_group.accuracy, 4),
            "best_performing_group": best_group.group.label(),
            "best_group_accuracy": round(best_group.accuracy, 4),
            "mean_accuracy": round(statistics.mean(accuracies), 4),
            "std_accuracy": round(statistics.stdev(accuracies), 4),
            "max_calibration_gap": round(max(calibration_gaps), 4),
            "group_count": len(group_performances),
        }

    def intersectional_matrix(self, group_performances: List[GroupPerformance]) -> Dict[str, float]:
        """Returns pairwise disparity across all group intersections."""
        matrix = {}
        for a, b in combinations(group_performances, 2):
            key = f"{a.group.label()} vs {b.group.label()}"
            matrix[key] = round(abs(a.accuracy - b.accuracy), 4)
        return matrix
