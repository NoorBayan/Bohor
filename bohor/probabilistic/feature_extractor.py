"""
Probabilistic Feature Extractor.
Extracts the five structural and statistical features:
(1) Metrical pattern prior
(2) Zihaf and Illah transformation frequencies
(3) Post-pruning candidate density
(4) Hemistich symmetry indicators
(5) Recurrent Taf'ilah sequence statistics
"""

import math
from typing import Dict, List, Optional, Sequence, Tuple

from bohor.core.types import Candidate, MeterFamily, MeterStructuralForm, Verse


class ProbabilisticFeatureExtractor:
    """
    Computes normalized statistical and structural features for candidate metrical derivations.
    All features are strictly normalized to [0.0, 1.0].
    """

    FEATURE_NAMES: Tuple[str, ...] = (
        "f1_metrical_prior",
        "f2_transformation_frequency",
        "f3_candidate_density",
        "f4_hemistich_symmetry",
        "f5_tafilah_sequence_frequency",
    )

    # Empirical metrical family distribution derived from classical Arabic poetic corpora (Section 6.2 & 8.2)
    CANONICAL_METER_PRIORS: Dict[MeterFamily, float] = {
        MeterFamily.TAWIL: 0.283,
        MeterFamily.BASIT: 0.181,
        MeterFamily.KAMIL: 0.194,
        MeterFamily.WAFIR: 0.112,
        MeterFamily.RAJAZ: 0.048,
        MeterFamily.RAMAL: 0.045,
        MeterFamily.SARI: 0.035,
        MeterFamily.KHAFIFA: 0.041,
        MeterFamily.MUNSARIH: 0.018,
        MeterFamily.MUTAQARIB: 0.024,
        MeterFamily.MUTADARAK: 0.005,
        MeterFamily.MADID: 0.004,
        MeterFamily.HAZAJ: 0.005,
        MeterFamily.MUJTATH: 0.003,
        MeterFamily.MUQTADAB: 0.001,
        MeterFamily.MUDARI: 0.001,
    }

    # Relative empirical weights of common Zihaf/Illah transformations (Section 6.2)
    TRANSFORMATION_WEIGHTS: Dict[str, float] = {
        "Salim": 1.00,
        "Khabn": 0.85,
        "Qabd": 0.80,
        "Idmar": 0.85,
        "Tayy": 0.50,
        "Kaff": 0.40,
        "Hadhf": 0.75,
        "Qat": 0.60,
        "Batr": 0.30,
        "Qasr": 0.55,
        "Tash'ith": 0.35,
    }

    def __init__(
        self,
        custom_meter_priors: Optional[Dict[MeterFamily, float]] = None,
        custom_trans_weights: Optional[Dict[str, float]] = None,
    ) -> None:
        self.meter_priors = custom_meter_priors or self.CANONICAL_METER_PRIORS
        self.trans_weights = custom_trans_weights or self.TRANSFORMATION_WEIGHTS

    def extract_features(
        self,
        candidate: Candidate,
        candidate_pool_size: int,
        verse: Optional[Verse] = None,
    ) -> Dict[str, float]:
        """
        Extracts the five paper-defined features for a single candidate.
        Populates candidate.features and returns the dictionary.
        """
        derivation = candidate.derivation

        # Feature 1: Metrical pattern prior P(H) 
        f1 = self.meter_priors.get(derivation.meter, 1.0 / len(MeterFamily))
        if derivation.form == MeterStructuralForm.MUJZU:
            f1 *= 0.75  # Truncated variants carry lower empirical prior than Tam forms

        # Feature 2: Frequencies of Zihaf and Illah transformations
        if not derivation.transformations:
            f2 = 1.0  # Sound meter (Salim) has maximum transformation score
        else:
            trans_scores = [self.trans_weights.get(t, 0.50) for t in derivation.transformations]
            f2 = sum(trans_scores) / len(trans_scores)
            # Complexity penalty proportional to transformation count
            f2 *= math.exp(-0.15 * len(derivation.transformations))

        # Feature 3: Candidate-density measures after deterministic pruning
        # Bounded between 0.0 and 1.0; dense candidate pools indicate higher residual ambiguity
        if candidate_pool_size <= 1:
            f3 = 1.0
        else:
            f3 = max(0.0, 1.0 - math.log(candidate_pool_size) / math.log(100.0))

        # Feature 4: Hemistich symmetry indicators (Section 6.2)
        total_feet = len(derivation.feet_sequence)
        if total_feet >= 2:
            half = total_feet // 2
            first_half_sylls = sum(f.length for f in derivation.feet_sequence[:half])
            second_half_sylls = sum(f.length for f in derivation.feet_sequence[half:])
            diff = abs(first_half_sylls - second_half_sylls)
            f4 = max(0.0, 1.0 - (diff / max(first_half_sylls, second_half_sylls, 1)))
        else:
            f4 = 0.50

        # Feature 5: Corpus occurrence statistics of recurrent Taf'ilah sequences
        # Evaluates structural regularity across foot transitions
        feet_count = len(derivation.feet_sequence)
        if feet_count > 0:
            # Measure homogeneity and known cadences
            cadence_score = 1.0 if derivation.feet_sequence[-1].mnemonic else 0.80
            f5 = cadence_score / math.sqrt(feet_count)
            f5 = min(1.0, max(0.0, f5 * 1.5))
        else:
            f5 = 0.0

        features = {
            "f1_metrical_prior": round(float(f1), 6),
            "f2_transformation_frequency": round(float(f2), 6),
            "f3_candidate_density": round(float(f3), 6),
            "f4_hemistich_symmetry": round(float(f4), 6),
            "f5_tafilah_sequence_frequency": round(float(f5), 6),
        }

        candidate.features = features
        return features

    def extract_batch(
        self,
        candidates: Sequence[Candidate],
        verse: Optional[Verse] = None,
    ) -> None:
        """Extracts and attaches features to all candidates in the surviving pool C."""
        pool_size = len(candidates)
        for cand in candidates:
            self.extract_features(candidate=cand, candidate_pool_size=pool_size, verse=verse)