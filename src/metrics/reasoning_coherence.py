"""
Reasoning Coherence Score (RCS)

Automated evaluation of clinical reasoning chain quality.
Measures HOW a model reasons, not just whether its final answer is correct.
Uses NLI (Natural Language Inference) + clinical ontology matching.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ReasoningStep:
    text: str
    step_type: str          # "observation" | "hypothesis" | "evidence" | "conclusion"
    evidence_level: Optional[str] = None  # "I" | "II" | "III" | "IV" | "V"
    references: List[str] = field(default_factory=list)


@dataclass
class ReasoningChain:
    steps: List[ReasoningStep]
    final_answer: str
    uncertainty_expressed: bool = False
    uncertainty_appropriate: bool = False


class ReasoningCoherenceScore:
    """
    RCS evaluates five dimensions of clinical reasoning quality:

    1. Logical consistency    (0–20): Steps do not contradict each other
    2. Evidence linkage       (0–20): Conclusions tied to cited evidence
    3. Ontology alignment     (0–20): Correct use of clinical terminology/ontology
    4. Uncertainty calibration(0–20): Model appropriately expresses/withholds uncertainty
    5. Conclusion validity    (0–20): Final answer follows from reasoning chain

    RCS = sum of five dimension scores (0–100)
    """

    def compute(self, chain: ReasoningChain) -> dict:
        scores = {
            "logical_consistency": self._score_logical_consistency(chain),
            "evidence_linkage": self._score_evidence_linkage(chain),
            "ontology_alignment": self._score_ontology_alignment(chain),
            "uncertainty_calibration": self._score_uncertainty(chain),
            "conclusion_validity": self._score_conclusion(chain),
        }

        rcs = sum(scores.values())
        evidence_levels = [
            s.evidence_level for s in chain.steps if s.evidence_level
        ]

        return {
            "rcs": rcs,
            "dimension_scores": scores,
            "grade": self._grade(rcs),
            "step_count": len(chain.steps),
            "evidence_levels_used": list(set(evidence_levels)),
            "uncertainty_expressed": chain.uncertainty_expressed,
        }

    def _score_logical_consistency(self, chain: ReasoningChain) -> float:
        # Placeholder: production impl uses NLI model to check step-step entailment
        steps_with_types = [s for s in chain.steps if s.step_type in ("hypothesis", "conclusion")]
        if not steps_with_types:
            return 10.0
        return 18.0  # Stub — replace with NLI-based scoring

    def _score_evidence_linkage(self, chain: ReasoningChain) -> float:
        evidence_steps = [s for s in chain.steps if s.step_type == "evidence"]
        if not evidence_steps:
            return 5.0
        with_refs = [s for s in evidence_steps if s.references]
        return round(20.0 * (len(with_refs) / len(evidence_steps)), 2)

    def _score_ontology_alignment(self, chain: ReasoningChain) -> float:
        # Placeholder: production impl uses SNOMED-CT / ICD-10 / UMLS term matching
        return 15.0  # Stub — replace with ontology matching

    def _score_uncertainty(self, chain: ReasoningChain) -> float:
        if chain.uncertainty_expressed and chain.uncertainty_appropriate:
            return 20.0
        elif not chain.uncertainty_expressed and not chain.uncertainty_appropriate:
            return 20.0  # Correctly omitted uncertainty
        elif chain.uncertainty_expressed and not chain.uncertainty_appropriate:
            return 8.0   # Over-hedging
        return 5.0       # Failed to express warranted uncertainty

    def _score_conclusion(self, chain: ReasoningChain) -> float:
        # Placeholder: production impl checks conclusion against prior steps via NLI
        conclusion_steps = [s for s in chain.steps if s.step_type == "conclusion"]
        return 18.0 if conclusion_steps else 5.0

    def _grade(self, rcs: float) -> str:
        if rcs >= 90:
            return "Excellent"
        elif rcs >= 75:
            return "Good"
        elif rcs >= 60:
            return "Acceptable"
        elif rcs >= 45:
            return "Poor"
        return "Failing"
