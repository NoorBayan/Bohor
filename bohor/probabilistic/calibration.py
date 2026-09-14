"""
Probability Calibration Engine.
"""

import math
from typing import List, Sequence, Tuple


class ProbabilityCalibrator:
    """
    Calibrates candidate score distributions via temperature-scaled Softmax.
    """

    DEFAULT_TEMPERATURE: float = 1.6

    def __init__(self, temperature: float = DEFAULT_TEMPERATURE) -> None:
        if temperature <= 0.0:
            raise ValueError(f"Temperature T must be strictly positive, got {temperature}")
        self.temperature = temperature

    def softmax(self, scores: Sequence[float], temperature: Optional[float] = None) -> List[float]:
        """
        Computes numerically stable temperature-scaled Softmax distribution.
        Uses subtract-max to prevent floating-point overflow.
        """
        if not scores:
            return []

        t = temperature if temperature is not None else self.temperature
        if t <= 0.0:
            raise ValueError(f"Temperature T must be strictly positive, got {t}")

        scaled_scores = [s / t for s in scores]
        max_score = max(scaled_scores)

        # Numerically stable exponentiation
        exp_scores = [math.exp(s - max_score) for s in scaled_scores]
        sum_exp = sum(exp_scores)

        if sum_exp == 0.0 or math.isnan(sum_exp):
            # Uniform fallback in degenerate zero-sum state
            uniform_prob = 1.0 / len(scores)
            return [uniform_prob for _ in scores]

        return [exp_val / sum_exp for exp_val in exp_scores]

    @staticmethod
    def compute_ece(
        confidences: Sequence[float],
        accuracies: Sequence[bool],
        num_bins: int = 10,
    ) -> float:
        """
        Calculates Expected Calibration Error (ECE) across partitioned probability bins:
        """
        n = len(confidences)
        if n == 0:
            return 0.0
        if len(accuracies) != n:
            raise ValueError(f"Mismatched lengths: {n} confidences vs {len(accuracies)} accuracies")
        if num_bins <= 0:
            raise ValueError(f"num_bins must be positive, got {num_bins}")

        bin_boundaries = [i / num_bins for i in range(num_bins + 1)]
        ece = 0.0

        for b in range(num_bins):
            lower = bin_boundaries[b]
            upper = bin_boundaries[b + 1]

            # Collect indices in current bin: [lower, upper) or [lower, upper] for final bin
            bin_indices = [
                idx
                for idx, conf in enumerate(confidences)
                if (lower <= conf < upper) or (b == num_bins - 1 and lower <= conf <= upper)
            ]

            bin_size = len(bin_indices)
            if bin_size > 0:
                bin_acc = sum(1.0 for idx in bin_indices if accuracies[idx]) / bin_size
                bin_conf = sum(confidences[idx] for idx in bin_indices) / bin_size
                ece += (bin_size / n) * abs(bin_acc - bin_conf)

        return round(float(ece), 6)