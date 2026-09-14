"""
Repository-Guided Candidate Generation and DAG Construction Engine.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from bohor.core.types import Candidate, Derivation, Verse
from bohor.deterministic.constraints import ProsodicConstraintMatrix
from bohor.deterministic.context_cache import PoemContextCache
from bohor.deterministic.repository import PatternRecord, PatternRepository


@dataclass
class DAGNode:
    """
    Shared intermediate derivation node within the Directed Acyclic Graph.
    Enables pointer traversal and structural sharing across competing derivations.
    """

    state_id: int
    step: int
    syllable_code: int
    ref_count: int = 1
    children: Dict[int, "DAGNode"] = field(default_factory=dict)

    def add_or_reuse_child(self, state_id: int, step: int, syllable_code: int) -> "DAGNode":
        """Reuses existing identical sub-graph node to avoid redundant allocations."""
        if syllable_code in self.children:
            child = self.children[syllable_code]
            child.ref_count += 1
            return child
        new_node = DAGNode(state_id=state_id, step=step, syllable_code=syllable_code)
        self.children[syllable_code] = new_node
        return new_node

    def prune_child(self, syllable_code: int) -> None:
        """Immediately deallocates invalid search branch (Early memory deallocation)."""
        if syllable_code in self.children:
            child = self.children[syllable_code]
            child.ref_count -= 1
            if child.ref_count <= 0:
                del self.children[syllable_code]


class ProsodicDAG:
    """
    Compact Directed Acyclic Graph representing the admissible candidate search space.
    """

    def __init__(self) -> None:
        self.root = DAGNode(state_id=0, step=0, syllable_code=-1)
        self._node_counter: int = 1

    def insert_or_reuse(self, current: DAGNode, step: int, syllable_code: int) -> DAGNode:
        """Algorithm 1: InsertOrReuseNode(G, State_i)."""
        node = current.add_or_reuse_child(state_id=self._node_counter, step=step, syllable_code=syllable_code)
        self._node_counter += 1
        return node

    def prune_branch(self, parent: DAGNode, syllable_code: int) -> None:
        """Algorithm 1: PruneBranch(G, CurrentNode)."""
        parent.prune_child(syllable_code)

    def clear(self) -> None:
        self.root.children.clear()
        self._node_counter = 1


@dataclass
class DAGSearchResult:
    """Output container for Algorithm 1."""

    candidates: List[Candidate]
    initial_pool_size: int
    pruned_count: int
    dag_nodes_count: int


class DAGBuilder:
    def __init__(
        self,
        repository: PatternRepository,
        constraint_matrix: Optional[ProsodicConstraintMatrix] = None,
        context_cache: Optional[PoemContextCache] = None,
    ) -> None:
        self.repository = repository
        self.constraints = constraint_matrix or ProsodicConstraintMatrix()
        self.context_cache = context_cache

    def build_candidate_space(
        self,
        footprint: str,
        verse: Optional[Verse] = None,
        poem_id: Optional[str] = None,
    ) -> DAGSearchResult:
        """
        Executes Algorithm 1:
        Phase 1: Indexed Retrieval -> Phase 2: State Expansion and Constraint Pruning.
        """
        if not self.repository.is_loaded:
            return DAGSearchResult(candidates=[], initial_pool_size=0, pruned_count=0, dag_nodes_count=0)

        # Algorithm 1: Phase 1 - Indexed Retrieval
        initial_pool: List[PatternRecord] = []

        # Check document-level context cache (Section 7.3)
        if poem_id and self.context_cache:
            cached_context = self.context_cache.lookup(poem_id)
            if cached_context:
                cached_meter, cached_form = cached_context
                # Restricted repository query bypassing exhaustive search
                initial_pool = [
                    rec for rec in self.repository.query_by_meter(cached_meter)
                    if rec.pattern_string == footprint or footprint in rec.pattern_string
                ]

        # Standard primary footprint query if cache missed
        if not initial_pool:
            initial_pool = self.repository.query_by_footprint(footprint)

        initial_pool_size = len(initial_pool)
        if initial_pool_size == 0:
            # Deterministic rejection (Out-of-scope/Anomalous)
            return DAGSearchResult(candidates=[], initial_pool_size=0, pruned_count=0, dag_nodes_count=0)

        # Algorithm 1: Phase 2 - State Expansion and Constraint Pruning
        dag = ProsodicDAG()
        admissible_records: List[PatternRecord] = []
        pruned_count = 0

        for pattern in initial_pool:
            is_valid = True
            current_node = dag.root
            pattern_bits = [(pattern.bitmask >> i) & 1 for i in range(pattern.length - 1, -1, -1)]

            # Step-by-step constraint verification and DAG state construction
            for step, bit in enumerate(pattern_bits):
                # Evaluate constraint decision function Phi(State_i, V)
                if not self.constraints.evaluate_candidate(pattern, verse):
                    # Violates structural or compatibility axioms -> Prune branch immediately
                    dag.prune_branch(current_node, bit)
                    is_valid = False
                    pruned_count += 1
                    break

                # Share DAG substructures across identical prefix paths
                current_node = dag.insert_or_reuse(current_node, step=step, syllable_code=bit)

            if is_valid:
                admissible_records.append(pattern)

        # Convert surviving records to domain Candidate objects
        # Deterministic sorting: meter value -> form -> pattern -> transformations count
        admissible_records.sort(
            key=lambda r: (r.meter.value, r.form.value, r.pattern_string, len(r.transformations))
        )

        candidates: List[Candidate] = []
        for rec in admissible_records:
            derivation_obj = rec.to_derivation()
            candidates.append(Candidate(derivation=derivation_obj))

        return DAGSearchResult(
            candidates=candidates,
            initial_pool_size=initial_pool_size,
            pruned_count=pruned_count,
            dag_nodes_count=dag._node_counter,
        )