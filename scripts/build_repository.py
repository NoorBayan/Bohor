"""
Offline Repository Generation Script.
Generates the precompiled metrical pattern repository from classical Arabic prosodic
axioms and transformation algebra.
Emits canonical CSV files directly consumable by bohor.deterministic.PatternRepository.
"""

import argparse
import csv
import itertools
import os
import sys
from typing import Dict, List, Set, Tuple

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bohor.core.algebra import TransformationAlgebra
from bohor.core.types import MeterFamily, MeterStructuralForm, SyllableType
from bohor.deterministic.repository import PatternRepository
from bohor.deterministic.vector_encoder import BitwiseVectorEncoder


class RepositoryBuilder:
    """
    Synthesizes mathematically admissible metrical configurations across the
    16 canonical meters and their 24 Tam and Mujzu' structural configurations.
    """

    S = SyllableType.SHORT.arud_symbol  # 'v'
    L = SyllableType.LONG.arud_symbol   # '-'

    # Admissible foot realizations under canonical Zihaf and Illah transformations
    # (Section 3.1, 3.2, and canonical prosodic treatises)
    TAFILAH_VARIATIONS: Dict[str, Dict[str, str]] = {
        "Fa'ulun": {
            "Salim": f"{S} {L} {L}",        # v - -
            "Qabd": f"{S} {L} {S}",         # v - v
            "Hadhf": f"{S} {L}",            # v -
            "Batr": f"{L}",                 # -
            "Qasr": f"{S} {L} {L}",         # v - - (terminal sukun pause)
        },
        "Mafa'ilun": {
            "Salim": f"{S} {L} {L} {L}",    # v - - -
            "Qabd": f"{S} {L} {S} {L}",     # v - v -
            "Kaff": f"{S} {L} {L} {S}",     # v - - v
            "Hadhf": f"{S} {L} {L}",        # v - -
        },
        "Mustaf'ilun": {
            "Salim": f"{L} {L} {S} {L}",    # - - v -
            "Khabn": f"{S} {L} {S} {L}",    # v - v -
            "Tayy": f"{L} {S} {S} {L}",     # - v v -
            "Khabl": f"{S} {S} {S} {L}",    # v v v -
            "Qat": f"{L} {L} {L}",          # - - -
            "Tadyil": f"{L} {L} {S} {L} {L}", # - - v - -
        },
        "Fa'ilun": {
            "Salim": f"{L} {S} {L}",        # - v -
            "Khabn": f"{S} {S} {L}",        # v v -
            "Qat": f"{L} {L}",              # - -
            "Tash'ith": f"{L} {L}",         # - -
        },
        "Mutafa'ilun": {
            "Salim": f"{S} {S} {L} {S} {L}", # v v - v -
            "Idmar": f"{L} {L} {S} {L}",     # - - v -
            "Waqas": f"{S} {S} {S} {L}",     # v v v -
            "Qat": f"{S} {S} {L} {L}",       # v v - -
            "Hadhaz": f"{S} {S} {L}",        # v v -
            "Tarfil": f"{S} {S} {L} {S} {L} {L}", # v v - v - -
        },
        "Mufa'alatun": {
            "Salim": f"{S} {L} {S} {S} {L}", # v - v v -
            "Asb": f"{S} {L} {L} {L}",       # v - - -
            "Aql": f"{S} {L} {S} {L}",       # v - v -
            "Qatf": f"{S} {L} {L}",          # v - -
        },
        "Fa'ilatun": {
            "Salim": f"{L} {S} {L} {L}",    # - v - -
            "Khabn": f"{S} {S} {L} {L}",    # v v - -
            "Kaff": f"{L} {S} {L} {S}",     # - v - v
            "Shakl": f"{S} {S} {L} {S}",    # v v - v
            "Hadhf": f"{L} {S} {L}",        # - v -
            "Batr": f"{L} {L}",             # - -
        },
        "Maf'ulatu": {
            "Salim": f"{L} {L} {L} {S}",    # - - - v
            "Khabn": f"{S} {L} {L} {S}",    # v - - v
            "Tayy": f"{L} {S} {L} {S}",     # - v - v
            "Khabl": f"{S} {S} {L} {S}",    # v v - v
            "Waqf": f"{L} {L} {L} {L}",     # - - - -
            "Kasf": f"{L} {L} {L}",         # - - -
        },
    }

    # Meter definitions: canonical foot templates for Sadr and Ajuz (Section 3.1 & 8.3)
    CANONICAL_CONFIGURATIONS: List[Tuple[MeterFamily, MeterStructuralForm, Tuple[str, ...]]] = [
        # Tawil (Tam only: 4 feet per hemistich)
        (MeterFamily.TAWIL, MeterStructuralForm.TAM, ("Fa'ulun", "Mafa'ilun", "Fa'ulun", "Mafa'ilun") * 2),
        # Basit (Tam: 4 feet, Mujzu': 3 feet)
        (MeterFamily.BASIT, MeterStructuralForm.TAM, ("Mustaf'ilun", "Fa'ilun", "Mustaf'ilun", "Fa'ilun") * 2),
        (MeterFamily.BASIT, MeterStructuralForm.MUJZU, ("Mustaf'ilun", "Fa'ilun", "Mustaf'ilun") * 2),
        # Kamil (Tam: 3 feet, Mujzu': 2 feet)
        (MeterFamily.KAMIL, MeterStructuralForm.TAM, ("Mutafa'ilun", "Mutafa'ilun", "Mutafa'ilun") * 2),
        (MeterFamily.KAMIL, MeterStructuralForm.MUJZU, ("Mutafa'ilun", "Mutafa'ilun") * 2),
        # Wafir (Tam: 3 feet, Mujzu': 2 feet)
        (MeterFamily.WAFIR, MeterStructuralForm.TAM, ("Mufa'alatun", "Mufa'alatun", "Fa'ulun") * 2),
        (MeterFamily.WAFIR, MeterStructuralForm.MUJZU, ("Mufa'alatun", "Mufa'alatun") * 2),
        # Rajaz (Tam: 3 feet, Mujzu': 2 feet)
        (MeterFamily.RAJAZ, MeterStructuralForm.TAM, ("Mustaf'ilun", "Mustaf'ilun", "Mustaf'ilun") * 2),
        (MeterFamily.RAJAZ, MeterStructuralForm.MUJZU, ("Mustaf'ilun", "Mustaf'ilun") * 2),
        # Ramal (Tam: 3 feet, Mujzu': 2 feet)
        (MeterFamily.RAMAL, MeterStructuralForm.TAM, ("Fa'ilatun", "Fa'ilatun", "Fa'ilatun") * 2),
        (MeterFamily.RAMAL, MeterStructuralForm.MUJZU, ("Fa'ilatun", "Fa'ilatun") * 2),
        # Sari' (Tam: 3 feet)
        (MeterFamily.SARI, MeterStructuralForm.TAM, ("Mustaf'ilun", "Mustaf'ilun", "Maf'ulatu") * 2),
        # Munsarih (Tam: 3 feet)
        (MeterFamily.MUNSARIH, MeterStructuralForm.TAM, ("Mustaf'ilun", "Maf'ulatu", "Mustaf'ilun") * 2),
        # Khafif (Tam: 3 feet, Mujzu': 2 feet)
        (MeterFamily.KHAFIFA, MeterStructuralForm.TAM, ("Fa'ilatun", "Mustaf'ilun", "Fa'ilatun") * 2),
        (MeterFamily.KHAFIFA, MeterStructuralForm.MUJZU, ("Fa'ilatun", "Mustaf'ilun") * 2),
        # Mudari' (Mujzu' only)
        (MeterFamily.MUDARI, MeterStructuralForm.MUJZU, ("Mafa'ilun", "Fa'ilatun") * 2),
        # Muqtadab (Mujzu' only)
        (MeterFamily.MUQTADAB, MeterStructuralForm.MUJZU, ("Maf'ulatu", "Mustaf'ilun") * 2),
        # Mujtath (Mujzu' only)
        (MeterFamily.MUJTATH, MeterStructuralForm.MUJZU, ("Mustaf'ilun", "Fa'ilatun") * 2),
        # Mutaqarib (Tam: 4 feet, Mujzu': 3 feet)
        (MeterFamily.MUTAQARIB, MeterStructuralForm.TAM, ("Fa'ulun", "Fa'ulun", "Fa'ulun", "Fa'ulun") * 2),
        (MeterFamily.MUTAQARIB, MeterStructuralForm.MUJZU, ("Fa'ulun", "Fa'ulun", "Fa'ulun") * 2),
        # Mutadarak (Tam: 4 feet, Mujzu': 3 feet)
        (MeterFamily.MUTADARAK, MeterStructuralForm.TAM, ("Fa'ilun", "Fa'ilun", "Fa'ilun", "Fa'ilun") * 2),
        (MeterFamily.MUTADARAK, MeterStructuralForm.MUJZU, ("Fa'ilun", "Fa'ilun", "Fa'ilun") * 2),
        # Madid (Mujzu': 3 feet)
        (MeterFamily.MADID, MeterStructuralForm.MUJZU, ("Fa'ilatun", "Fa'ilun", "Fa'ilatun") * 2),
        # Hazaj (Mujzu': 2 feet)
        (MeterFamily.HAZAJ, MeterStructuralForm.MUJZU, ("Mafa'ilun", "Mafa'ilun") * 2),
    ]

    def __init__(self) -> None:
        self.algebra = TransformationAlgebra()

    def generate_all_patterns(self) -> List[Dict[str, str]]:
        """
        Synthesizes the complete admissible metrical space via cartesian product
        of allowable transformations, filtered by prosodic compatibility constraints.
        """
        records: List[Dict[str, str]] = []
        seen_patterns: Set[Tuple[str, str, str]] = set()
        pattern_id = 1

        for meter_enum, form_enum, template_feet in self.CANONICAL_CONFIGURATIONS:
            # Prepare transformation options for each foot position
            num_feet = len(template_feet)
            half_feet = num_feet // 2

            feet_options: List[List[Tuple[str, str, str]]] = []
            for idx, foot_name in enumerate(template_feet):
                is_terminal = (idx == half_feet - 1) or (idx == num_feet - 1)
                variations = self.TAFILAH_VARIATIONS.get(foot_name, {"Salim": ""})

                options: List[Tuple[str, str, str]] = []
                for trans_name, syll_pat in variations.items():
                    # Illah transformations are strictly reserved for terminal feet (Arud and Darb)
                    if trans_name in ("Hadhf", "Batr", "Qat", "Qasr", "Tadyil", "Tarfil", "Qatf", "Kasf", "Waqf"):
                        if not is_terminal:
                            continue
                    options.append((foot_name, trans_name, syll_pat))
                feet_options.append(options)

            # Cartesian product of allowable transformations across feet
            for combination in itertools.product(*feet_options):
                # Check compatibility constraints across adjacent feet
                trans_names = [t[1] for t in combination if t[1] != "Salim"]
                
                # Verify mutual exclusivity of transformations
                compatible = True
                for i in range(len(trans_names)):
                    for j in range(i + 1, len(trans_names)):
                        if not self.algebra.are_compatible(trans_names[i], trans_names[j]):
                            compatible = False
                            break
                    if not compatible:
                        break
                if not compatible:
                    continue

                full_pattern = " ".join(t[2] for t in combination)
                full_feet = " ".join(t[0] for t in combination)
                full_trans = ", ".join(trans_names) if trans_names else "Salim"

                dedup_key = (meter_enum.value, form_enum.value, full_pattern)
                if dedup_key in seen_patterns:
                    continue
                seen_patterns.add(dedup_key)

                records.append({
                    "pattern_id": str(pattern_id),
                    "meter": meter_enum.value,
                    "form": form_enum.value,
                    "pattern": full_pattern,
                    "feet": full_feet,
                    "transformations": full_trans,
                })
                pattern_id += 1

        # Sort deterministically by meter, form, and pattern
        records.sort(key=lambda r: (r["meter"], r["form"], r["pattern"]))
        return records


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Offline Generation of the Precompiled Metrical Pattern Repository (Bohor)."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="corpus/precompiled/bohor_patterns.csv",
        help="Target CSV output path.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing repository file if present.",
    )
    args = parser.parse_args()

    output_path = os.path.abspath(args.output)
    if os.path.exists(output_path) and not args.force:
        sys.stderr.write(f"Error: Output file already exists: {output_path}. Use --force to overwrite.\n")
        return 1

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    sys.stderr.write("Synthesizing admissible metrical patterns across 16 canonical meters...\n")
    builder = RepositoryBuilder()
    records = builder.generate_all_patterns()

    sys.stderr.write(f"Generated {len(records)} admissible metrical configurations.\n")
    sys.stderr.write(f"Writing to: {output_path}...\n")

    fieldnames = ["pattern_id", "meter", "form", "pattern", "feet", "transformations"]
    with open(output_path, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    # Validate output by testing with PatternRepository
    sys.stderr.write("Validating generated repository via bohor.deterministic.PatternRepository...\n")
    repo = PatternRepository()
    repo.load_from_csv(output_path)
    sys.stderr.write(f"Validation successful: Loaded {repo.total_patterns} patterns with intact indices.\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())