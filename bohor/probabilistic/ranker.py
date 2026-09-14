"""
Probabilistic Candidate Ranker.
Multi-criteria candidate scoring, temperature-scaled
Softmax normalization, and deterministic tie-breaking.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from bohor.core.types import Candidate
from bohor.probabilistic.calibration import ProbabilityCalibrator
from bohor.probabilistic.feature_extractor import ProbabilisticFeatureExtractor


@dataclass(frozen=True)
class RankingResult:
    """Container for candidate ranking execution."""

    optimal_candidate: Optional[Candidate]
    ranked_candidates: List[Candidate]
    top_score: float
    top_probability: float
    probability_margin: float


class ProbabilisticRanker:
    """
    Executes candidate ranking and deterministic tie-breaking.
    Score(c) = sum_{j=1}^m w_j * f_j(c)
    """

    # Feature interpolation weights estimated on disjoint validation subset (Section 6.3)
    DEFAULT_WEIGHTS: Dict[str, float] = {
        "f1_metrical_prior": 0.30,
        "f2_transformation_frequency": 0.25,
        "f3_candidate_density": 0.15,
        "f4_hemistich_symmetry": 0.15,
        "f5_tafilah_sequence_frequency": 0.15,
    }

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        calibrator: Optional[ProbabilityCalibrator] = None,
    ) -> None:
        self.weights = weights or self.DEFAULT_WEIGHTS
        self.calibrator = calibrator or ProbabilityCalibrator()

    def rank(self, candidates: Sequence[Candidate]) -> RankingResult:
        """
        Scores candidates, breaks ties deterministically by minimum transformation count,
        and applies temperature-scaled Softmax.
        """
        # Algorithm 2, Phase 1: Base Case Handling
        if not candidates:
            return RankingResult(
                optimal_candidate=None,
                ranked_candidates=[],
                top_score=0.0,
                top_probability=0.0,
                probability_margin=0.0,
            )

        if len(candidates) == 1:
            single = candidates[0]
            score = self._compute_score(single)
            single.raw_score = score
            single.posterior_probability = 1.0
            single.calibrated_probability = 1.0
            return RankingResult(
                optimal_candidate=single,
                ranked_candidates=[single],
                top_score=score,
                top_probability=1.0,
                probability_margin=1.0,
            )

        # Algorithm 2, Phase 2: Scoring and Sorting
        candidate_list = list(candidates)
        for cand in candidate_list:
            cand.raw_score = self._compute_score(cand)

        # Algorithm 2, Phase 3: Deterministic Tie-Breaking
        # Primary key: Raw score (descending)
        # Secondary key: Minimum transformations count (ascending) -> argmin CountProsodicTransformations
        # Tertiary key: Canonical meter name and pattern string for stable reproducibility
        candidate_list.sort(
            key=lambda c: (
                -c.raw_score,
                c.transformations_count,
                c.meter.value,
                c.derivation.pattern_string,
            )
        )

        # Algorithm 2, Phase 4: Temperature-Scaled Softmax Calibration
        raw_scores = [c.raw_score for c in candidate_list]
        calibrated_probs = self.calibrator.softmax(raw_scores)

        for idx, prob in enumerate(calibrated_probs):
            candidate_list[idx].calibrated_probability = prob
            candidate_list[idx].posterior_probability = prob

        top_cand = candidate_list[0]
        second_cand = candidate_list[1]
        top_prob = top_cand.calibrated_probability
        margin = top_prob - second_cand.calibrated_probability

        return RankingResult(
            optimal_candidate=top_cand,
            ranked_candidates=candidate_list,
            top_score=top_cand.raw_score,
            top_probability=top_prob,
            probability_margin=margin,
        )

    def _compute_score(self, candidate: Candidate) -> float:
        """Computes weighted linear combination: Score(c) = sum_j w_j * f_j(c)."""
        score = 0.0
        for feat_name, weight in self.weights.items():
            feat_val = candidate.features.get(feat_name, 0.0)
            score += weight * feat_val
        return float(score)