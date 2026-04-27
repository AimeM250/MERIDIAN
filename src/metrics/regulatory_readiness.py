"""
Regulatory Readiness Score (RRS)

Maps MERIDIAN evaluation results directly to FDA pre-submission readiness.
Creates a documented bridge between benchmark performance and the regulatory pathway.

Aligned with:
  - FDA Good Machine Learning Practice (GMLP) for Medical Device Development
  - FDA Predetermined Change Control Plan (PCCP) guidance
  - EU AI Act Annex III (High-Risk AI Systems — Healthcare)
  - ONC 21st Century Cures Act interoperability requirements
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RegulatoryComponent:
    name: str
    weight: float           # 0.0 – 1.0, must sum to 1.0 across all components
    score: float            # 0 – 100
    evidence: str           # What evidence supports this score
    gaps: List[str] = field(default_factory=list)


class RegulatoryReadinessScore:
    """
    RRS Components (FDA GMLP + EU AI Act alignment):

    1. Intended Use Clarity         (15%) — Is the clinical indication well-defined?
    2. Performance Evidence         (25%) — Is there sufficient validation data?
    3. Bias & Equity Documentation  (20%) — Is demographic performance documented?
    4. Transparency & Explainability(15%) — Can outputs be explained to clinicians?
    5. Post-Market Monitoring Plan  (15%) — Is there a drift/degradation plan?
    6. Algorithm Change Control     (10%) — Is the PCCP defined?

    RRS = Σ(component_score_i × weight_i)
    """

    COMPONENTS = [
        ("intended_use_clarity", 0.15),
        ("performance_evidence", 0.25),
        ("bias_equity_documentation", 0.20),
        ("transparency_explainability", 0.15),
        ("post_market_monitoring", 0.15),
        ("algorithm_change_control", 0.10),
    ]

    def compute(self, components: List[RegulatoryComponent]) -> dict:
        if abs(sum(c.weight for c in components) - 1.0) > 0.001:
            raise ValueError("Component weights must sum to 1.0")

        rrs = sum(c.score * c.weight for c in components)
        all_gaps = [gap for c in components for gap in c.gaps]

        return {
            "rrs": round(rrs, 2),
            "readiness_tier": self._tier(rrs),
            "fda_submission_ready": rrs >= 75.0,
            "eu_ai_act_ready": rrs >= 80.0,
            "component_scores": {c.name: round(c.score, 2) for c in components},
            "critical_gaps": all_gaps,
            "gap_count": len(all_gaps),
        }

    def _tier(self, rrs: float) -> str:
        if rrs >= 85:
            return "Pre-submission ready"
        elif rrs >= 70:
            return "Near-ready — minor gaps"
        elif rrs >= 55:
            return "Foundational — significant gaps"
        return "Early stage — major gaps"
