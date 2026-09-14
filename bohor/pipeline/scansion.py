"""
Single-Verse Scansion Pipeline Coordinator.
staged workflow, strictly isolating deterministic validation from probabilistic ranking.
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from bohor.core.exceptions import (
    BohorException,
    TypeIIIConstraintError,
    TypeIVSearchError,
)
from bohor.core.types import (
    Candidate,
    Derivation,
    MeterFamily,
    MeterStructuralForm,
    Verse,
)
from bohor.deterministic.constraints import ProsodicConstraintMatrix
from bohor.deterministic.context_cache import PoemContextCache
from bohor.deterministic.dag_builder import DAGBuilder, DAGSearchResult
from bohor.deterministic.repository import PatternRepository
from bohor.preprocessing.normalizer import TextNormalizer
from bohor.preprocessing.syllabifier import ProsodicSyllabifier
from bohor.probabilistic.calibration import ProbabilityCalibrator
from bohor.probabilistic.feature_extractor import ProbabilisticFeatureExtractor
from bohor.probabilistic.hitl_router import (
    ConfidenceRoutingResult,
    HITLRouter,
    RoutingDecision,
)
from bohor.probabilistic.ranker import ProbabilisticRanker, RankingResult


@dataclass(frozen=True)
class ScansionResult:
    """
    Structured, auditable scansion output preserving the entire derivational pathway,
    feature valuations, calibration statistics, and uncertainty routing decisions
    """

    raw_text: str
    verse_id: Optional[str] = None
    poem_id: Optional[str] = None
    status: str = "SUCCESS"  # SUCCESS, REJECTED_OUT_OF_SCOPE, ERROR

    # Preprocessing representations
    normalized_sadr: str = ""
    normalized_ajuz: str = ""
    footprint: str = ""

    # Derivational resolution (None if rejected or failed)
    optimal_derivation: Optional[Derivation] = None
    meter: Optional[MeterFamily] = None
    structural_form: Optional[MeterStructuralForm] = None
    tafilat: Tuple[str, ...] = field(default_factory=tuple)
    transformations: Tuple[str, ...] = field(default_factory=tuple)
    pattern_string: str = ""

    # Probabilistic and calibration metrics
    raw_score: float = 0.0
    calibrated_probability: float = 0.0
    probability_margin: float = 0.0
    normalized_entropy: float = 0.0
    features: Dict[str, float] = field(default_factory=dict)

    # Uncertainty and routing outcome
    routing_decision: RoutingDecision = RoutingDecision.DETERMINISTIC_REJECTION
    is_autonomous: bool = False

    # Search space diagnostics
    initial_pool_size: int = 0
    pruned_candidates_count: int = 0
    surviving_candidates_count: int = 0
    dag_nodes_count: int = 0
    error_message: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.status == "SUCCESS" and self.optimal_derivation is not None


class VerseScansionPipeline:
    """
    Orchestrates the complete single-verse prosodic scansion pipeline:
    Preprocessing -> Deterministic Bounding -> Probabilistic Ranking -> Uncertainty Routing.
    """

    def __init__(
        self,
        repository: PatternRepository,
        normalizer: Optional[TextNormalizer] = None,
        syllabifier: Optional[ProsodicSyllabifier] = None,
        constraint_matrix: Optional[ProsodicConstraintMatrix] = None,
        context_cache: Optional[PoemContextCache] = None,
        feature_extractor: Optional[ProbabilisticFeatureExtractor] = None,
        ranker: Optional[ProbabilisticRanker] = None,
        router: Optional[HITLRouter] = None,
    ) -> None:
        self.repository = repository
        self.normalizer = normalizer or TextNormalizer()
        self.syllabifier = syllabifier or ProsodicSyllabifier(normalizer=self.normalizer)
        self.constraints = constraint_matrix or ProsodicConstraintMatrix()
        self.context_cache = context_cache
        self.dag_builder = DAGBuilder(
            repository=self.repository,
            constraint_matrix=self.constraints,
            context_cache=self.context_cache,
        )
        self.feature_extractor = feature_extractor or ProbabilisticFeatureExtractor()
        self.ranker = ranker or ProbabilisticRanker()
        self.router = router or HITLRouter()

    def scan_verse(
        self,
        verse_text: str,
        verse_id: Optional[str] = None,
        poem_id: Optional[str] = None,
    ) -> ScansionResult:
        """
        Executes end-to-end scansion on a single verse text.
        Preserves complete stage boundaries and diagnostics without throwing
        uncaught exceptions on validly rejectable inputs.
        """
        if not verse_text or not verse_text.strip():
            return ScansionResult(
                raw_text=verse_text,
                verse_id=verse_id,
                poem_id=poem_id,
                status="ERROR",
                error_message="Empty or whitespace-only verse string",
                routing_decision=RoutingDecision.DETERMINISTIC_REJECTION,
            )

        # Stage 1: Preprocessing & Morpho-phonological Syllabification
        try:
            verse_obj, footprint = self.syllabifier.process_verse_into_units(
                raw_verse=verse_text,
                verse_id=verse_id,
            )
            sadr_norm = verse_obj.first_hemistich.raw_text
            ajuz_norm = verse_obj.second_hemistich.raw_text
        except TypeIVSearchError as e:
            return ScansionResult(
                raw_text=verse_text,
                verse_id=verse_id,
                poem_id=poem_id,
                status="ERROR",
                error_message=f"Type IV Search Error: {e.message}",
                routing_decision=RoutingDecision.DETERMINISTIC_REJECTION,
            )
        except Exception as e:
            return ScansionResult(
                raw_text=verse_text,
                verse_id=verse_id,
                poem_id=poem_id,
                status="ERROR",
                error_message=f"Preprocessing failure: {str(e)}",
                routing_decision=RoutingDecision.DETERMINISTIC_REJECTION,
            )

        # Stage 2: Deterministic Search Space Bounding (Algorithm 1)
        search_result: DAGSearchResult = self.dag_builder.build_candidate_space(
            footprint=footprint,
            verse=verse_obj,
            poem_id=poem_id,
        )

        candidates = search_result.candidates
        if not candidates:
            # Deterministic rejection: verse is metrically invalid or non-canonical (Section 8.5)
            return ScansionResult(
                raw_text=verse_text,
                verse_id=verse_id,
                poem_id=poem_id,
                status="REJECTED_OUT_OF_SCOPE",
                normalized_sadr=sadr_norm,
                normalized_ajuz=ajuz_norm,
                footprint=footprint,
                initial_pool_size=search_result.initial_pool_size,
                pruned_candidates_count=search_result.pruned_count,
                surviving_candidates_count=0,
                dag_nodes_count=search_result.dag_nodes_count,
                routing_decision=RoutingDecision.DETERMINISTIC_REJECTION,
            )

        # Stage 3: Probabilistic Disambiguation & Ranking (Algorithm 2)
        # 3a. Extract the 5 normalized features over candidate set C exclusively
        self.feature_extractor.extract_batch(candidates=candidates, verse=verse_obj)

        # 3b. Weighted scoring and deterministic tie-breaking
        ranking_result: RankingResult = self.ranker.rank(candidates=candidates)

        # Stage 4: Uncertainty Quantification and HITL Routing (Section 6.4)
        routing_result: ConfidenceRoutingResult = self.router.evaluate(ranking_result=ranking_result)

        optimal_cand = routing_result.optimal_candidate
        if optimal_cand is None:
            return ScansionResult(
                raw_text=verse_text,
                verse_id=verse_id,
                poem_id=poem_id,
                status="REJECTED_OUT_OF_SCOPE",
                normalized_sadr=sadr_norm,
                normalized_ajuz=ajuz_norm,
                footprint=footprint,
                routing_decision=RoutingDecision.DETERMINISTIC_REJECTION,
            )

        derivation = optimal_cand.derivation

        # Stage 5: Contextual Cache Update (Section 7.3)
        # Lock document-level meter if confident prediction was reached
        if poem_id and self.context_cache and routing_result.is_autonomous:
            self.context_cache.store(
                poem_id=poem_id,
                meter=derivation.meter,
                form=derivation.form,
                confidence=routing_result.top_probability,
            )

        # Extract textual Taf'ilah representations
        tafilat_names = tuple(f.mnemonic for f in derivation.feet_sequence)

        return ScansionResult(
            raw_text=verse_text,
            verse_id=verse_id,
            poem_id=poem_id,
            status="SUCCESS",
            normalized_sadr=sadr_norm,
            normalized_ajuz=ajuz_norm,
            footprint=footprint,
            optimal_derivation=derivation,
            meter=derivation.meter,
            structural_form=derivation.form,
            tafilat=tafilat_names,
            transformations=derivation.transformations,
            pattern_string=derivation.pattern_string,
            raw_score=optimal_cand.raw_score,
            calibrated_probability=routing_result.top_probability,
            probability_margin=routing_result.probability_margin,
            normalized_entropy=routing_result.normalized_entropy,
            features=optimal_cand.features,
            routing_decision=routing_result.decision,
            is_autonomous=routing_result.is_autonomous,
            initial_pool_size=search_result.initial_pool_size,
            pruned_candidates_count=search_result.pruned_count,
            surviving_candidates_count=len(candidates),
            dag_nodes_count=search_result.dag_nodes_count,
        )