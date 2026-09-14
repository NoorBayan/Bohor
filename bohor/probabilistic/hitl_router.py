"""
Human-in-the-Loop (HITL) Uncertainty Router.
normalized Shannon entropy, probability margin computation,
and selective classification routing.
"""

import math
from dataclasses import dataclass
from enum import Enum, unique
from typing import List, Optional, Sequence

from bohor.core.types import Candidate
from bohor.probabilistic.ranker import RankingResult


@unique
class RoutingDecision(Enum):
    """Routing outcome for scansion candidates (Section 6.4)."""

    ACCEPTED_HIGH_CONFIDENCE = "High Confidence"
    REFERRED_TO_HITL = "Low Confidence"
    DETERMINISTIC_REJECTION = "Deterministic Rejection"


@dataclass(frozen=True)
class ConfidenceRoutingResult:
    """Detailed decision outcome from the HITL router."""

    decision: RoutingDecision
    optimal_candidate: Optional[Candidate]
    top_probability: float
    probability_margin: float
    normalized_entropy: float
    is_autonomous: bool


class HITLRouter:
    """
    Uncertainty quantification and selective classification router.
    Routes predictions to expert review if top calibrated probability < tau (0.70)
    or probability margin < theta (Section 6.4 & Algorithm 2).
    """

    DEFAULT_TAU: float = 0.70     # Absolute confidence threshold (Section 6.4)
    DEFAULT_THETA: float = 0.10   # Nearest competitor probability margin threshold

    def __init__(
        self,
        tau: float = DEFAULT_TAU,
        theta: float = DEFAULT_THETA,
    ) -> None:
        if not (0.0 <= tau <= 1.0):
            raise ValueError(f"Threshold tau must be in [0, 1], got {tau}")
        if not (0.0 <= theta <= 1.0):
            raise ValueError(f"Threshold theta must be in [0, 1], got {theta}")
        self.tau = tau
        self.theta = theta

    def evaluate(self, ranking_result: RankingResult) -> ConfidenceRoutingResult:
        """
        Evaluates uncertainty metrics on calibrated candidates:
        Computes Normalized Shannon Entropy and Margin, applying routing policy.
        """
        candidates = ranking_result.ranked_candidates
        num_candidates = len(candidates)

        # Base case: deterministic rejection
        if num_candidates == 0 or ranking_result.optimal_candidate is None:
            return ConfidenceRoutingResult(
                decision=RoutingDecision.DETERMINISTIC_REJECTION,
                optimal_candidate=None,
                top_probability=0.0,
                probability_margin=0.0,
                normalized_entropy=0.0,
                is_autonomous=False,
            )

        # Base case: zero structural ambiguity
        if num_candidates == 1:
            return ConfidenceRoutingResult(
                decision=RoutingDecision.ACCEPTED_HIGH_CONFIDENCE,
                optimal_candidate=ranking_result.optimal_candidate,
                top_probability=1.0,
                probability_margin=1.0,
                normalized_entropy=0.0,
                is_autonomous=True,
            )

        probabilities = [c.calibrated_probability for c in candidates]
        entropy = self.compute_normalized_entropy(probabilities)
        top_prob = ranking_result.top_probability
        margin = ranking_result.probability_margin

        # Routing Policy (Section 6.4 & Algorithm 2, Phase 4)
        # Prediction deferred to expert review if top probability < tau OR margin < theta
        if top_prob < self.tau or margin < self.theta:
            decision = RoutingDecision.REFERRED_TO_HITL
            is_autonomous = False
        else:
            decision = RoutingDecision.ACCEPTED_HIGH_CONFIDENCE
            is_autonomous = True

        return ConfidenceRoutingResult(
            decision=decision,
            optimal_candidate=ranking_result.optimal_candidate,
            top_probability=round(top_prob, 6),
            probability_margin=round(margin, 6),
            normalized_entropy=round(entropy, 6),
            is_autonomous=is_autonomous,
        )

    @staticmethod
    def compute_normalized_entropy(probabilities: Sequence[float]) -> float:
        """
        Calculates Normalized Shannon Entropy:
        H(X) = -1 / ln(|C|) * sum_{i=1}^|C| p(c_i | X) * ln(p(c_i | X)) (Section 6.4).
        Bounded strictly between 0.0 (certainty) and 1.0 (uniform uncertainty).
        """
        k = len(probabilities)
        if k <= 1:
            return 0.0

        entropy_sum = 0.0
        for p in probabilities:
            if p > 1e-12:
                entropy_sum += p * math.log(p)

        max_entropy = math.log(k)
        if max_entropy == 0.0:
            return 0.0

        normalized_h = -entropy_sum / max_entropy
        # Clamp against floating point inaccuracy
        return max(0.0, min(1.0, float(normalized_h)))