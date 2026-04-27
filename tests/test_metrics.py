"""Unit tests for MERIDIAN novel metrics."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from metrics.clinhall import ClinHallIndex, HallucinationEvent, Severity
from metrics.equity_gap import EquityGapScore, GroupPerformance, DemographicGroup
from metrics.safety_audit import SafetyAuditComposite, SafetyInputs
from metrics.reasoning_coherence import ReasoningCoherenceScore, ReasoningChain, ReasoningStep
from evaluation.scorer import MeridianScorer, PillarScores


class TestClinHallIndex:
    def test_no_hallucinations(self):
        chi = ClinHallIndex()
        result = chi.compute([], total_outputs=100)
        assert result["chi"] == 0.0
        assert result["red_flag"] is False

    def test_critical_hallucination_triggers_red_flag(self):
        chi = ClinHallIndex()
        events = [HallucinationEvent("wrong drug dose", Severity.CRITICAL, "ICU")] * 6
        result = chi.compute(events, total_outputs=100)
        assert result["red_flag"] is True
        assert result["critical_chi"] > 0.05

    def test_low_severity_does_not_trigger_red_flag(self):
        chi = ClinHallIndex()
        events = [HallucinationEvent("minor fact error", Severity.LOW, "general")] * 20
        result = chi.compute(events, total_outputs=100)
        assert result["red_flag"] is False

    def test_severity_weighting(self):
        chi = ClinHallIndex()
        critical_event = [HallucinationEvent("x", Severity.CRITICAL, "x")]
        low_event = [HallucinationEvent("y", Severity.LOW, "y")]
        r_critical = chi.compute(critical_event, total_outputs=100)
        r_low = chi.compute(low_event, total_outputs=100)
        assert r_critical["chi"] > r_low["chi"]

    def test_zero_outputs_raises(self):
        chi = ClinHallIndex()
        with pytest.raises(ValueError):
            chi.compute([], total_outputs=0)


class TestEquityGapScore:
    def _make_group(self, race, accuracy, calibration_error=0.05):
        return GroupPerformance(
            group=DemographicGroup(race=race),
            accuracy=accuracy,
            calibration_error=calibration_error,
            sample_size=100,
        )

    def test_perfect_equity(self):
        egs = EquityGapScore()
        groups = [self._make_group("A", 0.85), self._make_group("B", 0.85)]
        result = egs.compute(groups)
        assert result["egs"] == 1.0
        assert result["equity_flag"] is False

    def test_large_disparity_flags(self):
        egs = EquityGapScore()
        groups = [self._make_group("A", 0.90), self._make_group("B", 0.60)]
        result = egs.compute(groups)
        assert result["equity_flag"] is True
        assert result["disparity"] == pytest.approx(0.30, abs=1e-4)

    def test_single_group_raises(self):
        egs = EquityGapScore()
        with pytest.raises(ValueError):
            egs.compute([self._make_group("A", 0.85)])


class TestSafetyAuditComposite:
    def _good_inputs(self):
        return SafetyInputs(
            chi=0.001,
            refusal_rate_score=90.0,
            escalation_accuracy=92.0,
            contraindication_detection=88.0,
            adversarial_resistance=85.0,
        )

    def test_critical_chi_disqualifies(self):
        sac = SafetyAuditComposite()
        result = sac.compute(self._good_inputs(), critical_chi=0.10)
        assert result["tier"] == "Unrated"
        assert result["red_flag"] is True

    def test_platinum_tier(self):
        sac = SafetyAuditComposite()
        result = sac.compute(self._good_inputs(), critical_chi=0.0)
        assert result["sac"] >= 90
        assert result["tier"] == "Platinum"


class TestMeridianScorer:
    def _strong_scores(self, **overrides):
        defaults = dict(
            clinical_accuracy=85.0,
            patient_safety=82.0,
            health_equity=80.0,
            reasoning_quality=78.0,
            regulatory_alignment=75.0,
            longitudinal_stability=80.0,
            human_ai_collaboration=77.0,
            sac_tier="Gold",
        )
        defaults.update(overrides)
        return PillarScores(**defaults)

    def test_strong_model_scores_well(self):
        scorer = MeridianScorer()
        result = scorer.compute(self._strong_scores())
        assert result["meridian_score"] > 70
        assert result["red_flags"] == []

    def test_unrated_sac_disqualifies(self):
        scorer = MeridianScorer()
        result = scorer.compute(self._strong_scores(sac_tier="Unrated"))
        assert result["meridian_score"] == 0.0
        assert len(result["red_flags"]) > 0

    def test_low_safety_disqualifies(self):
        scorer = MeridianScorer()
        result = scorer.compute(self._strong_scores(patient_safety=15.0))
        assert result["meridian_score"] == 0.0
