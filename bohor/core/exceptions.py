# FILE: bohor/core/exceptions.py
"""
Exception hierarchy for the Bohor prosody system.
"""

from typing import Optional


class BohorException(Exception):
    """Base class for all exceptions raised by the Bohor pipeline."""

    def __init__(self, message: str, verse_text: Optional[str] = None) -> None:
        super().__init__(message)
        self.message = message
        self.verse_text = verse_text

    def __str__(self) -> str:
        if self.verse_text:
            return f"{self.message} | Context Verse: '{self.verse_text}'"
        return self.message


class TypeIClassificationError(BohorException):
    """
    Type I Failure: The deterministic engine bounds the search space correctly,
    but the probabilistic ranker selects a metrical family that fundamentally
    contradicts the true underlying ground-truth meter (Section 9.1).
    """

    def __init__(
        self,
        message: str,
        predicted_meter: str,
        expected_meter: Optional[str] = None,
        verse_text: Optional[str] = None,
    ) -> None:
        detail = f"{message} (Predicted: {predicted_meter}, Expected: {expected_meter})"
        super().__init__(detail, verse_text)
        self.predicted_meter = predicted_meter
        self.expected_meter = expected_meter


class TypeIIRankingError(BohorException):
    """
    Type II Failure: The true metrical derivation is successfully generated
    and exists within the admissible search space, but it is incorrectly
    down-ranked below a structurally similar competitor (Section 9.1).
    """

    def __init__(
        self,
        message: str,
        top_ranked_pattern: str,
        gold_pattern: str,
        verse_text: Optional[str] = None,
    ) -> None:
        detail = f"{message} (Top Candidate: '{top_ranked_pattern}', Target Gold: '{gold_pattern}')"
        super().__init__(detail, verse_text)
        self.top_ranked_pattern = top_ranked_pattern
        self.gold_pattern = gold_pattern


class TypeIIIConstraintError(BohorException):
    """
    Type III Failure: The deterministic constraint matrix Phi(V, M) is overly
    restrictive, rejecting a valid (or highly irregular/non-canonical) verse
    structure during early state evaluation (Section 5.3 & 9.1).
    """

    def __init__(
        self,
        message: str,
        meter: str,
        violated_constraint: str,
        verse_text: Optional[str] = None,
    ) -> None:
        detail = f"{message} [Meter: {meter}, Constraint: {violated_constraint}]"
        super().__init__(detail, verse_text)
        self.meter = meter
        self.violated_constraint = violated_constraint


class TypeIVSearchError(BohorException):
    """
    Type IV Failure: The input string contains unrecoverable typographical or
    orthographic corruption, preventing the syllabification layer from generating
    a valid signature and halting graph expansion entirely (Section 9.1).
    """

    def __init__(
        self,
        message: str,
        unparsed_token: Optional[str] = None,
        verse_text: Optional[str] = None,
    ) -> None:
        detail = f"{message} (Unparsed Token: '{unparsed_token}')" if unparsed_token else message
        super().__init__(detail, verse_text)
        self.unparsed_token = unparsed_token


class RepositoryFormatError(BohorException):
    """Raised when pattern database or precompiled repository files are corrupted or invalid."""


class CorpusDataError(BohorException):
    """Raised when ingested corpus files fail structural, encoding, or format validation."""


class ConfigurationError(BohorException):
    """Raised when runtime hyperparameter configurations (e.g. tau, T, weights) are invalid."""