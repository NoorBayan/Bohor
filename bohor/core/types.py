
from dataclasses import dataclass, field
from enum import Enum, unique
from typing import Any, Dict, List, Optional, Sequence, Tuple


@unique
class SyllableType(Enum):
    """
    Elementary syllabic categories: S = {sigma_short, sigma_long, sigma_overlong}
    defined in Section 3.1.
    """

    SHORT = "S"        # Mutaharrik (Short: e.g. Ba) -> Weight: 1 mora
    LONG = "L"         # Sabab Khafif (Consonant + Vowel + Sukun: e.g. Qam) -> 2 morae
    OVERLONG = "O"     # Overlong syllable occurring at hemistich pauses -> >=3 morae

    @property
    def binary_code(self) -> int:
        """Binary representation for vectorized bitwise pattern matching (Section 7.2)."""
        if self == SyllableType.SHORT:
            return 0
        if self == SyllableType.LONG:
            return 1
        return 1  # Overlong is mapped to heavy terminal weight in binary representation

    @property
    def arud_symbol(self) -> str:
        """Traditional prosodic notation symbol."""
        if self == SyllableType.SHORT:
            return "v"
        if self == SyllableType.LONG:
            return "-"
        return "~"


@unique
class MeterFamily(Enum):
    """The 16 canonical metrical families established by Al-Khalil (Section 3.1 & 8.2)."""

    TAWIL = "Tawil"
    BASIT = "Basit"
    KAMIL = "Kamil"
    WAFIR = "Wafir"
    RAJAZ = "Rajaz"
    RAMAL = "Ramal"
    SARI = "Sari"
    MUNSARIH = "Munsarih"
    KHAFIFA = "Khafif"
    MUDARI = "Mudari"
    MUQTADAB = "Muqtadab"
    MUJTATH = "Mujtath"
    MUTAQARIB = "Mutaqarib"
    MUTADARAK = "Mutadarak"
    MADID = "Madid"
    HAZAJ = "Hazaj"

    @classmethod
    def from_arabic_name(cls, name: str) -> "MeterFamily":
        """Maps standard Arabic meter names to the enum."""
        mapping = {
            "الطويل": cls.TAWIL,
            "البسيط": cls.BASIT,
            "الكامل": cls.KAMIL,
            "الوافر": cls.WAFIR,
            "الرجز": cls.RAJAZ,
            "الرمل": cls.RAMAL,
            "السريع": cls.SARI,
            "المنسرح": cls.MUNSARIH,
            "الخفيف": cls.KHAFIFA,
            "المضارع": cls.MUDARI,
            "المقتضب": cls.MUQTADAB,
            "المجتث": cls.MUJTATH,
            "المتقارب": cls.MUTAQARIB,
            "المتدارك": cls.MUTADARAK,
            "المديد": cls.MADID,
            "الهزج": cls.HAZAJ,
        }
        normalized = name.strip()
        if normalized in mapping:
            return mapping[normalized]
        for member in cls:
            if member.value.lower() == normalized.lower():
                return member
        raise ValueError(f"Unknown meter name: '{name}'")


@unique
class MeterStructuralForm(Enum):
    """Structural meter configurations: Full (Tam) or Truncated (Mujzu') (Section 8.3)."""

    TAM = "Tam"
    MUJZU = "Mujzu"
    MASHTUR = "Mashtur"
    MANHUK = "Manhuk"


@unique
class AmbiguityType(Enum):
    """
    Four-fold ambiguity classification: A = {A_o, A_m, A_p, A_r}
    defined in Section 6.1.
    """

    ORTHOGRAPHIC_UNDERSPECIFICATION = "A_o"  # Missing diacritics
    MORPHOLOGICAL_AMBIGUITY = "A_m"          # Competing lexical segmentations
    PHONOLOGICAL_VARIATION = "A_p"           # Alternative phonetic realizations
    PROSODIC_MULTIPLICITY = "A_r"            # Single sequence matching multiple meters


@dataclass(frozen=True)
class Syllable:
    """Atomic phonetic-prosodic syllable with structural properties."""

    phonetic_text: str
    syllable_type: SyllableType

    def __str__(self) -> str:
        return self.syllable_type.arud_symbol


@dataclass(frozen=True)
class ProsodicFoot:
    """
    Represents a metrical foot (Taf'ilah) T = (sigma_1, ..., sigma_k)
    within the canonical lexicon T (Section 3.1).
    """

    mnemonic: str                                    # e.g., 'Fa'ulun', 'Mafa'ilun'
    syllables: Tuple[SyllableType, ...]
    transformations: Tuple[str, ...] = field(default_factory=tuple)  # Applied Zihaf/Illah

    @property
    def pattern_string(self) -> str:
        """Returns standard prosodic notation string, e.g., 'v - -'."""
        return " ".join(s.arud_symbol for s in self.syllables)

    @property
    def binary_signature(self) -> int:
        """Vectorized bitwise integer representation."""
        val = 0
        for s in self.syllables:
            val = (val << 1) | s.binary_code
        return val

    @property
    def length(self) -> int:
        return len(self.syllables)


@dataclass(frozen=True)
class Hemistich:
    """
    Ordered sequence of metrical feet H = <T_1, T_2, ..., T_m>
    representing a single poetic shatr (Section 3.1).
    """

    feet: Tuple[ProsodicFoot, ...]
    raw_text: str = ""

    @property
    def foot_count(self) -> int:
        return len(self.feet)

    @property
    def pattern_string(self) -> str:
        return " | ".join(f.pattern_string for f in self.feet)

    @property
    def total_syllables(self) -> int:
        return sum(f.length for f in self.feet)


@dataclass(frozen=True)
class Verse:
    """
    Complete bipartite verse V = <H_left, H_right> (Sadr and Ajuz)
    defined in Section 3.1.
    """

    first_hemistich: Hemistich                      # Sadr
    second_hemistich: Hemistich                     # Ajuz
    verse_id: Optional[str] = None
    poet: Optional[str] = None
    era: Optional[str] = None

    @property
    def is_bipartite(self) -> bool:
        return self.second_hemistich.foot_count > 0


@dataclass(frozen=True)
class Derivation:
    """
    Structured prosodic derivation representing the complete auditable scansion:
    Meter + Structural Form + Ordered Taf'ilah sequence + Applied Transformations.
    (Section 2.2, 7.1, 8.4).
    """

    meter: MeterFamily
    form: MeterStructuralForm
    feet_sequence: Tuple[ProsodicFoot, ...]
    transformations: Tuple[str, ...]
    pattern_string: str
    binary_vector: Tuple[int, ...] = field(default_factory=tuple)

    @property
    def total_transformations_count(self) -> int:
        """Count of applied Zihaf and Illah operations used for deterministic tie-breaking."""
        return len(self.transformations)


@dataclass
class Candidate:
    """
    Candidate metrical hypothesis surviving deterministic filtering,
    passed to the probabilistic disambiguation layer (Section 6.2 & Algorithm 2).
    """

    derivation: Derivation
    features: Dict[str, float] = field(default_factory=dict)
    raw_score: float = 0.0
    posterior_probability: float = 0.0
    calibrated_probability: float = 0.0

    @property
    def meter(self) -> MeterFamily:
        return self.derivation.meter

    @property
    def transformations_count(self) -> int:
        return self.derivation.total_transformations_count