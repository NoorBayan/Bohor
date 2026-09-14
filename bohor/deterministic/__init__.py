"""
Deterministic Prosodic Engine for Bohor.
Implements precompiled pattern indexing, bitwise vector encoding, formal constraint
verification, early-pruned DAG search, and poem-level contextual caching
"""

from bohor.deterministic.constraints import ProsodicConstraintMatrix
from bohor.deterministic.context_cache import PoemContextCache
from bohor.deterministic.dag_builder import DAGBuilder, DAGSearchResult
from bohor.deterministic.repository import PatternRecord, PatternRepository
from bohor.deterministic.vector_encoder import BitwiseVectorEncoder

__all__ = [
    "BitwiseVectorEncoder",
    "PatternRecord",
    "PatternRepository",
    "ProsodicConstraintMatrix",
    "PoemContextCache",
    "DAGBuilder",
    "DAGSearchResult",
]
