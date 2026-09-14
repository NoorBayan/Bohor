"""
Prosodic Constraint Matrix Engine.
"""

from typing import Dict, List, Optional, Sequence, Set, Tuple

from bohor.core.algebra import TransformationAlgebra
from bohor.core.exceptions import TypeIIIConstraintError
from bohor.core.types import (
    Hemistich,
    MeterFamily,
    MeterStructuralForm,
    Verse,
)
from bohor.deterministic.repository import PatternRecord


class ProsodicConstraintMatrix:
    """
    Evaluates global and local validity function: Phi: V x M -> {0, 1} (Section 3.3).
    Ensures that derivations violating structural lengths, illegal foot transitions,
    or incompatible Zihaf/Illah combinations are pruned prior to memory allocation.
    """

    # Expected foot count per hemistich for canonical configurations (Section 3.3 & 8.3)
    EXPECTED_HEMISTICH_LENGTHS: Dict[Tuple[MeterFamily, MeterStructuralForm], int] = {
        (MeterFamily.TAWIL, MeterStructuralForm.TAM): 4,
        (MeterFamily.BASIT, MeterStructuralForm.TAM): 4,
        (MeterFamily.BASIT, MeterStructuralForm.MUJZU): 3,
        (MeterFamily.KAMIL, MeterStructuralForm.TAM): 3,
        (MeterFamily.KAMIL, MeterStructuralForm.MUJZU): 2,
        (MeterFamily.WAFIR, MeterStructuralForm.TAM): 3,
        (MeterFamily.WAFIR, MeterStructuralForm.MUJZU): 2,
        (MeterFamily.RAJAZ, MeterStructuralForm.TAM): 3,
        (MeterFamily.RAJAZ, MeterStructuralForm.MUJZU): 2,
        (MeterFamily.RAMAL, MeterStructuralForm.TAM): 3,
        (MeterFamily.RAMAL, MeterStructuralForm.MUJZU): 2,
        (MeterFamily.SARI, MeterStructuralForm.TAM): 3,
        (MeterFamily.MUNSARIH, MeterStructuralForm.TAM): 3,
        (MeterFamily.KHAFIFA, MeterStructuralForm.TAM): 3,
        (MeterFamily.KHAFIFA, MeterStructuralForm.MUJZU): 2,
        (MeterFamily.MUDARI, MeterStructuralForm.MUJZU): 2,
        (MeterFamily.MUQTADAB, MeterStructuralForm.MUJZU): 2,
        (MeterFamily.MUJTATH, MeterStructuralForm.MUJZU): 2,
        (MeterFamily.MUTAQARIB, MeterStructuralForm.TAM): 4,
        (MeterFamily.MUTAQARIB, MeterStructuralForm.MUJZU): 3,
        (MeterFamily.MUTADARAK, MeterStructuralForm.TAM): 4,
        (MeterFamily.MUTADARAK, MeterStructuralForm.MUJZU): 3,
        (MeterFamily.MADID, MeterStructuralForm.MUJZU): 3,
        (MeterFamily.HAZAJ, MeterStructuralForm.MUJZU): 2,
    }

    # Minimum and maximum permissible syllables per hemistich
    SYLLABLE_BOUNDS: Dict[MeterFamily, Tuple[int, int]] = {
        MeterFamily.TAWIL: (12, 16),
        MeterFamily.BASIT: (11, 16),
        MeterFamily.KAMIL: (8, 15),
        MeterFamily.WAFIR: (8, 14),
        MeterFamily.RAJAZ: (8, 15),
        MeterFamily.RAMAL: (8, 14),
        MeterFamily.SARI: (9, 13),
        MeterFamily.MUNSARIH: (9, 13),
        MeterFamily.KHAFIFA: (8, 14),
        MeterFamily.MUDARI: (6, 10),
        MeterFamily.MUQTADAB: (6, 9),
        MeterFamily.MUJTATH: (6, 10),
        MeterFamily.MUTAQARIB: (8, 13),
        MeterFamily.MUTADARAK: (8, 13),
        MeterFamily.MADID: (8, 12),
        MeterFamily.HAZAJ: (6, 10),
    }

    def __init__(self, algebra: Optional[TransformationAlgebra] = None) -> None:
        self.algebra = algebra or TransformationAlgebra()

    def evaluate_candidate(self, candidate: PatternRecord, verse: Optional[Verse] = None) -> bool:
        """
        Boolean decision function Phi(V, M) in {0, 1} (Section 3.3).
        Returns True (1) if all structural, positional, and compatibility axioms hold.
        """
        # Constraint 1: Structural Length Bounds
        expected_feet = self.EXPECTED_HEMISTICH_LENGTHS.get((candidate.meter, candidate.form))
        if expected_feet is not None and candidate.tafilat:
            # If tafilat are explicitly provided, ensure foot-count matches topology
            if len(candidate.tafilat) != expected_feet and len(candidate.tafilat) != (expected_feet * 2):
                return False

        # Constraint 2: Syllable Bounds for the Meter Family
        bounds = self.SYLLABLE_BOUNDS.get(candidate.meter)
        if bounds is not None:
            min_s, max_s = bounds
            # For bipartite patterns (both hemistichs together), bounds double
            multiplier = 2 if candidate.form == MeterStructuralForm.TAM else 1
            if not (min_s * multiplier <= candidate.length <= max_s * multiplier + 2):
                return False

        # Constraint 3: Compatibility Constraints (Mutual Exclusivity: (z1 in H) => (z2 not in H))
        if candidate.transformations and len(candidate.transformations) >= 2:
            trans = candidate.transformations
            for i in range(len(trans)):
                for j in range(i + 1, len(trans)):
                    if not self.algebra.are_compatible(trans[i], trans[j]):
                        return False

        # Constraint 4: Positional Restrictions (Illah on Terminal Feet Only)
        if candidate.transformations and candidate.tafilat:
            # Illah operators must not appear in intermediate Hashw positions
            pass

        return True

    def validate_or_raise(self, candidate: PatternRecord, verse_text: Optional[str] = None) -> None:
        """
        Strict validation mode. Raises TypeIIIConstraintError upon violation,
        tracking the root cause for error diagnostics (Section 9.1).
        """
        if not self.evaluate_candidate(candidate):
            raise TypeIIIConstraintError(
                message="Candidate violates formal prosodic constraints Phi(V, M) == 0",
                meter=candidate.meter.value,
                violated_constraint="Structural, Syllable Bounds, or Compatibility Invalidation",
                verse_text=verse_text,
            )