"""
Core domain models, transformation algebra, and exception hierarchies
for the formal representation of classical Arabic prosody.
"""

from bohor.core.algebra import (
    IllahOperator,
    ProsodicOperator,
    TransformationAlgebra,
    ZihafOperator,
)
from bohor.core.exceptions import (
    BohorException,
    ConfigurationError,
    CorpusDataError,
    RepositoryFormatError,
    TypeIClassificationError,
    TypeIIRankingError,
    TypeIIIConstraintError,
    TypeIVSearchError,
)
from bohor.core.types import (
    AmbiguityType,
    Candidate,
    Derivation,
    Hemistich,
    MeterFamily,
    MeterStructuralForm,
    ProsodicFoot,
    Syllable,
    SyllableType,
    Verse,
)

__all__ = [
    "SyllableType",
    "Syllable",
    "ProsodicFoot",
    "Hemistich",
    "Verse",
    "MeterFamily",
    "MeterStructuralForm",
    "Derivation",
    "Candidate",
    "AmbiguityType",
    "ProsodicOperator",
    "ZihafOperator",
    "IllahOperator",
    "TransformationAlgebra",
    "BohorException",
    "TypeIClassificationError",
    "TypeIIRankingError",
    "TypeIIIConstraintError",
    "TypeIVSearchError",
    "RepositoryFormatError",
    "CorpusDataError",
    "ConfigurationError",
]
