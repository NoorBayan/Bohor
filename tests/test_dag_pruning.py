"""
Unit Tests for DAG Construction and Constraint Pruning.
Validates structural node sharing, early memory deallocation, and deterministic
search space bounding to prevent OOM collapse.
"""

import unittest

from bohor.core.types import MeterFamily, MeterStructuralForm
from bohor.deterministic.constraints import ProsodicConstraintMatrix
from bohor.deterministic.dag_builder import DAGBuilder, DAGNode, ProsodicDAG
from bohor.deterministic.repository import PatternRecord, PatternRepository


class TestDAGPruning(unittest.TestCase):
    """Verifies that the DAG structure shares nodes and prunes invalid branches cleanly."""

    def setUp(self) -> None:
        self.dag = ProsodicDAG()
        self.repo = PatternRepository()
        self.constraints = ProsodicConstraintMatrix()
        self.builder = DAGBuilder(repository=self.repo, constraint_matrix=self.constraints)

    def test_structural_node_sharing(self) -> None:
        """Tests that paths sharing identical syllable prefixes reuse the same DAG nodes in memory."""
        root = self.dag.root
        # Path 1: Short (0) -> Long (1)
        node_s1 = self.dag.insert_or_reuse(root, step=0, syllable_code=0)
        node_l1 = self.dag.insert_or_reuse(node_s1, step=1, syllable_code=1)

        # Path 2: Short (0) -> Long (1) -> Short (0)
        # Step 0: should reuse node_s1 (ref_count increases)
        initial_ref = node_s1.ref_count
        node_s2 = self.dag.insert_or_reuse(root, step=0, syllable_code=0)
        self.assertEqual(node_s1, node_s2)
        self.assertEqual(node_s1.ref_count, initial_ref + 1)

    def test_early_branch_memory_deallocation(self) -> None:
        """Tests that pruning immediately detaches dead-end branches and deallocates children."""
        root = self.dag.root
        child_node = self.dag.insert_or_reuse(root, step=0, syllable_code=1)
        self.assertIn(1, root.children)

        # Prune branch
        self.dag.prune_branch(root, syllable_code=1)
        self.assertNotIn(1, root.children)

    def test_empty_repository_handling(self) -> None:
        """Tests Algorithm 1 base case: empty repository returns zero candidates without error."""
        result = self.builder.build_candidate_space(footprint="v - - v - - -")
        self.assertEqual(len(result.candidates), 0)
        self.assertEqual(result.initial_pool_size, 0)
        self.assertEqual(result.pruned_count, 0)

    def test_deterministic_candidate_ordering(self) -> None:
        """Tests that candidate retrieval ordering is 100% deterministic and reproducible."""
        rec1 = PatternRecord(
            pattern_id=1,
            meter=MeterFamily.TAWIL,
            form=MeterStructuralForm.TAM,
            pattern_string="v - - v - - -",
            bitmask=0b0110111,
            length=7,
            tafilat=("Fa'ulun", "Mafa'ilun"),
            transformations=("Salim",),
        )
        rec2 = PatternRecord(
            pattern_id=2,
            meter=MeterFamily.BASIT,
            form=MeterStructuralForm.TAM,
            pattern_string="v - - v - - -",
            bitmask=0b0110111,
            length=7,
            tafilat=("Mustaf'ilun", "Fa'ilun"),
            transformations=("Khabn",),
        )

        self.repo._records.extend([rec1, rec2])
        self.repo._index_record(rec1)
        self.repo._index_record(rec2)
        self.repo._is_loaded = True

        res1 = self.builder.build_candidate_space(footprint="v - - v - - -")
        res2 = self.builder.build_candidate_space(footprint="v - - v - - -")

        self.assertEqual(len(res1.candidates), len(res2.candidates))
        # Exact sequence equality
        for c1, c2 in zip(res1.candidates, res2.candidates):
            self.assertEqual(c1.meter, c2.meter)
            self.assertEqual(c1.derivation.pattern_string, c2.derivation.pattern_string)


if __name__ == "__main__":
    unittest.main()