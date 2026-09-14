"""
Probabilistic Disambiguation Engine for Bohor.
Implements feature extraction, weighted ranking, temperature calibration,
and uncertainty-based HITL routing over deterministic candidates
"""

from bohor.probabilistic.calibration import ProbabilityCalibrator
from bohor.probabilistic.feature_extractor import ProbabilisticFeatureExtractor
from bohor.probabilistic.hitl_router import ConfidenceRoutingResult, HITLRouter
from bohor.probabilistic.ranker import ProbabilisticRanker, RankingResult

__all__ = [
    "ProbabilisticFeatureExtractor",
    "ProbabilityCalibrator",
    "ProbabilisticRanker",
    "RankingResult",
    "HITLRouter",
    "ConfidenceRoutingResult",
]
