# FILE: tests/test_algebra.py
"""
Unit Tests for Transformation Algebra.
Validates functional composition, operator applicability, and mutual exclusivity
constraints between Zihaf and Illah operations.
"""

import unittest
from typing import Tuple

from bohor.core.algebra import (
    IllahOperator,
    ProsodicOperator,
    TransformationAlgebra,
    ZihafOperator,
)
from bohor.core.types import ProsodicFoot, SyllableType


class TestTransformationAlgebra(unittest.TestCase):
    """Tests algebraic operations and formal constraints over canonical prosodic feet."""

    def setUp(self) -> None:
        self.algebra = TransformationAlgebra()
        self.S = SyllableType.SHORT
        self.L = SyllableType.LONG

        # Canonical Fa'ulun foot: [v, -, -]
        self.faulun = ProsodicFoot(
            mnemonic="Fa'ulun",
            syllables=(self.S, self.L, self.L),
            transformations=(),
        )

        # Canonical Mustaf'ilun foot: [-, -, v, -]
        self.mustafilun = ProsodicFoot(
            mnemonic="Mustaf'ilun",
            syllables=(self.L, self.L, self.S, self.L),
            transformations=(),
        )

    def test_zihaf_application(self) -> None:
        """Tests that local Zihaf operators correctly transform target syllables and record metadata."""
        qabd_op = self.algebra.get_operator("Qabd")
        self.assertIsNotNone(qabd_op)
        self.assertTrue(isinstance(qabd_op, ZihafOperator))

        transformed = qabd_op.apply(self.faulun)
        # Qabd on Fa'ulun (v - -) deletes fifth quiescent letter -> Fa'ulu (v - v)
        self.assertEqual(transformed.syllables, (self.S, self.L, self.S))
        self.assertEqual(transformed.mnemonic, "Fa'ulu")
        self.assertIn("Qabd", transformed.transformations)

    def test_illah_positional_constraint(self) -> None:
        """Tests that position-sensitive Illah operators apply strictly to terminal feet."""
        hadhf_op = self.algebra.get_operator("Hadhf")
        self.assertIsNotNone(hadhf_op)
        self.assertTrue(isinstance(hadhf_op, IllahOperator))

        # Position 0 of 4 (Hashw - intermediate) -> should NOT be applicable
        self.assertFalse(hadhf_op.is_applicable(self.faulun, position_in_hemistich=0, total_feet=4))
        # Position 3 of 4 (Darb/Arud - terminal) -> applicable
        self.assertTrue(hadhf_op.is_applicable(self.faulun, position_in_hemistich=3, total_feet=4))

        transformed = hadhf_op.apply(self.faulun)
        # Hadhf on Fa'ulun (v - -) removes final Sabab Khafif -> Fa'u (v -)
        self.assertEqual(transformed.syllables, (self.S, self.L))
        self.assertIn("Hadhf", transformed.transformations)

    def test_functional_composition(self) -> None:
        """Tests composite transformations: (f2 o f1)(T) = f2(f1(T))."""
        khabn_op = ZihafOperator(
            name="TestKhabn",
            target_mnemonic="Mustaf'ilun",
            result_mnemonic="Muta'filun",
            target_syllables=(self.L, self.L, self.S, self.L),
            result_syllables=(self.S, self.L, self.S, self.L),
        )
        self.algebra.register_operator(khabn_op)

        step1 = khabn_op.apply(self.mustafilun)
        self.assertEqual(step1.syllables, (self.S, self.L, self.S, self.L))
        self.assertEqual(step1.transformations, ("TestKhabn",))

    def test_mutual_exclusivity_incompatibility(self) -> None:
        """Tests that mutually exclusive operators cannot be composed."""
        self.algebra.register_incompatibility("OpA", "OpB")
        self.assertFalse(self.algebra.are_compatible("OpA", "OpB"))
        self.assertFalse(self.algebra.are_compatible("OpB", "OpA"))

        # Unrestricted operators remain compatible
        self.assertTrue(self.algebra.are_compatible("OpA", "OpC"))


if __name__ == "__main__":
    unittest.main()
