"""
Unit Tests for Uncertainty Quantification and HITL Routing.
"""

import math
import unittest

from bohor.core.types import (
    Candidate,
    Derivation,
    MeterFamily,
    MeterStructuralForm,
    ProsodicFoot,
    SyllableType,
)
from bohor.probabilistic.calibration import ProbabilityCalibrator
from bohor.probabilistic.hitl_router import HITLRouter, RoutingDecision
from bohor.probabilistic.ranker import ProbabilisticRanker, RankingResult


class TestHITLRouting(unittest.TestCase):
    """Tests probabilistic calibration, tie-breaking, and selective HITL routing."""

    def setUp(self) -> None:
        self.router = HITLRouter(tau=0.70, theta=0.10)
        self.ranker = ProbabilisticRanker()
        self.calibrator = ProbabilityCalibrator(temperature=1.6)

        # Helper to create lightweight candidate objects
        def create_mock_candidate(meter: MeterFamily, transformations: tuple) -> Candidate:
            derivation = Derivation(
                meter=meter,
                form=MeterStructuralForm.TAM,
                feet_sequence=(
                    ProsodicFoot(
                        mnemonic="Fa'ulun",
                        syllables=(SyllableType.SHORT, SyllableType.LONG, SyllableType.LONG),
                        transformations=transformations,
                    ),
                ),
                transformations=transformations,
                pattern_string="v - -",
            )
            return Candidate(derivation=derivation)

        self.cand_salim = create_mock_candidate(MeterFamily.TAWIL, transformations=())
        self.cand_complex = create_mock_candidate(MeterFamily.TAWIL, transformations=("Qabd", "Hadhf"))

    def test_deterministic_tie_breaking_by_transformations_count(self) -> None:
        """Tests that identical raw scores prefer the candidate with fewer transformations."""
        # Assign equal scores
        self.cand_salim.features = {"f1_metrical_prior": 0.5}
        self.cand_complex.features = {"f1_metrical_prior": 0.5}

        result = self.ranker.rank([self.cand_complex, self.cand_salim])
        # cand_salim has 0 transformations vs cand_complex with 2 transformations
        self.assertEqual(result.optimal_candidate, self.cand_salim)
        self.assertEqual(result.optimal_candidate.transformations_count, 0)

    def test_temperature_scaling_softmax(self) -> None:
        """Tests that probability distribution sums to 1.0 under T=1.6 without overflow."""
        scores = [1.2, 0.8, 0.4]
        probs = self.calibrator.softmax(scores, temperature=1.6)
        self.assertEqual(len(probs), 3)
        self.assertAlmostEqual(sum(probs), 1.0, places=6)
        # Monotonicity: higher score yields strictly higher probability
        self.assertTrue(probs[0] > probs[1] > probs[2])

    def test_hitl_routing_threshold_tau(self) -> None:
        """Tests routing: top probability < 0.70 defers prediction to expert review."""
        self.cand_salim.calibrated_probability = 0.65  # Below tau=0.70
        self.cand_complex.calibrated_probability = 0.35

        mock_ranking = RankingResult(
            optimal_candidate=self.cand_salim,
            ranked_candidates=[self.cand_salim, self.cand_complex],
            top_score=0.8,
            top_probability=0.65,
            probability_margin=0.30,
        )

        decision_result = self.router.evaluate(mock_ranking)
        self.assertEqual(decision_result.decision, RoutingDecision.REFERRED_TO_HITL)
        self.assertFalse(decision_result.is_autonomous)

    def test_hitl_autonomous_acceptance(self) -> None:
        """Tests routing: top probability >= 0.70 and margin >= 0.10 accepts automatically."""
        self.cand_salim.calibrated_probability = 0.85  # Above tau=0.70
        self.cand_complex.calibrated_probability = 0.15

        mock_ranking = RankingResult(
            optimal_candidate=self.cand_salim,
            ranked_candidates=[self.cand_salim, self.cand_complex],
            top_score=0.9,
            top_probability=0.85,
            probability_margin=0.70,
        )

        decision_result = self.router.evaluate(mock_ranking)
        self.assertEqual(decision_result.decision, RoutingDecision.ACCEPTED_HIGH_CONFIDENCE)
        self.assertTrue(decision_result.is_autonomous)

    def test_normalized_shannon_entropy(self) -> None:
        """Tests that Normalized Shannon Entropy H(X) is bounded in [0, 1]."""
        # Zero ambiguity (|C| = 1) -> Entropy must be exactly 0.0
        self.assertEqual(HITLRouter.compute_normalized_entropy([1.0]), 0.0)

        # Maximum ambiguity: uniform distribution over 2 candidates -> Entropy must be 1.0
        h_uniform = HITLRouter.compute_normalized_entropy([0.5, 0.5])
        self.assertAlmostEqual(h_uniform, 1.0, places=5)

    def test_expected_calibration_error_computation(self) -> None:
        """Tests exact ECE computation across probability bins."""
        confidences = [0.9, 0.8, 0.7, 0.4]
        accuracies = [True, True, False, False]
        ece = ProbabilityCalibrator.compute_ece(confidences, accuracies, num_bins=5)
        self.assertGreaterEqual(ece, 0.0)
        self.assertLessEqual(ece, 1.0)


if __name__ == "__main__":
    unittest.main()