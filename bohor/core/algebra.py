"""
Transformation Algebra for classical Arabic prosody.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, unique
from typing import Callable, Dict, List, Optional, Set, Tuple

from bohor.core.types import ProsodicFoot, SyllableType


@unique
class OperatorScope(Enum):
    """Scope of prosodic modification: local to any foot, or terminal only."""

    LOCAL_ZIHAF = "Zihaf"       # Acts within a single foot (Section 3.2)
    TERMINAL_ILLAH = "Illah"    # Position-sensitive, terminal feet only (Section 3.2)


class ProsodicOperator(ABC):
    """
    Abstract operator f: T -> T' representing a single legal prosodic modification.
    """

    def __init__(
        self,
        name: str,
        scope: OperatorScope,
        description: str,
    ) -> None:
        self.name = name
        self.scope = scope
        self.description = description

    @abstractmethod
    def is_applicable(self, foot: ProsodicFoot, position_in_hemistich: int, total_feet: int) -> bool:
        """Determines if the structural preconditions of this operator are satisfied."""

    @abstractmethod
    def apply(self, foot: ProsodicFoot) -> ProsodicFoot:
        """Executes the deterministic transformation on the foot."""

    def __call__(self, foot: ProsodicFoot) -> ProsodicFoot:
        return self.apply(foot)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name} ({self.scope.value})>"


class ZihafOperator(ProsodicOperator):
    """
    Local operator z_i in Z acting within a single foot without modifying
    higher-level hemistich topology (Section 3.2).
    """

    def __init__(
        self,
        name: str,
        target_mnemonic: str,
        result_mnemonic: str,
        target_syllables: Tuple[SyllableType, ...],
        result_syllables: Tuple[SyllableType, ...],
        description: str = "",
    ) -> None:
        super().__init__(name=name, scope=OperatorScope.LOCAL_ZIHAF, description=description)
        self.target_mnemonic = target_mnemonic
        self.result_mnemonic = result_mnemonic
        self.target_syllables = target_syllables
        self.result_syllables = result_syllables

    def is_applicable(self, foot: ProsodicFoot, position_in_hemistich: int, total_feet: int) -> bool:
        return foot.syllables == self.target_syllables

    def apply(self, foot: ProsodicFoot) -> ProsodicFoot:
        if not self.is_applicable(foot, 0, 0):
            return foot
        updated_transformations = foot.transformations + (self.name,)
        return ProsodicFoot(
            mnemonic=self.result_mnemonic,
            syllables=self.result_syllables,
            transformations=updated_transformations,
        )


class IllahOperator(ProsodicOperator):
    """
    Position-sensitive operator i_j in I acting predominantly upon terminal
    feet ('Arud and Darb) (Section 3.2).
    """

    def __init__(
        self,
        name: str,
        target_mnemonic: str,
        result_mnemonic: str,
        target_syllables: Tuple[SyllableType, ...],
        result_syllables: Tuple[SyllableType, ...],
        terminal_only: bool = True,
        description: str = "",
    ) -> None:
        super().__init__(name=name, scope=OperatorScope.TERMINAL_ILLAH, description=description)
        self.target_mnemonic = target_mnemonic
        self.result_mnemonic = result_mnemonic
        self.target_syllables = target_syllables
        self.result_syllables = result_syllables
        self.terminal_only = terminal_only

    def is_applicable(self, foot: ProsodicFoot, position_in_hemistich: int, total_feet: int) -> bool:
        if self.terminal_only and position_in_hemistich < (total_feet - 1):
            return False
        return foot.syllables == self.target_syllables

    def apply(self, foot: ProsodicFoot) -> ProsodicFoot:
        updated_transformations = foot.transformations + (self.name,)
        return ProsodicFoot(
            mnemonic=self.result_mnemonic,
            syllables=self.result_syllables,
            transformations=updated_transformations,
        )


class TransformationAlgebra:
    """
    Algebraic functional composition engine (f_2 o f_1)(T) = f_2(f_1(T))
    ensuring that all derivations remain strictly bounded within the finite
    admissible metrical inventory (Section 3.2).
    """

    def __init__(self) -> None:
        self._operators: Dict[str, ProsodicOperator] = {}
        self._incompatible_pairs: Set[Tuple[str, str]] = set()
        self._initialize_canonical_operators()

    def register_operator(self, operator: ProsodicOperator) -> None:
        """Registers an operator in the algebraic inventory."""
        self._operators[operator.name] = operator

    def register_incompatibility(self, op1_name: str, op2_name: str) -> None:
        """
        Encodes mutual exclusivity constraint: (z_1 in H) => (z_2 not in H)
        defined in Section 3.3.
        """
        self._incompatible_pairs.add((op1_name, op2_name))
        self._incompatible_pairs.add((op2_name, op1_name))

    def are_compatible(self, op1_name: str, op2_name: str) -> bool:
        """Checks whether two operators can co-exist within the same foot/derivation."""
        return (op1_name, op2_name) not in self._incompatible_pairs

    def get_operator(self, name: str) -> Optional[ProsodicOperator]:
        return self._operators.get(name)

    def compose(
        self,
        first_op: ProsodicOperator,
        second_op: ProsodicOperator,
    ) -> Callable[[ProsodicFoot], ProsodicFoot]:
        """
        Functional composition of two operators: (f_2 o f_1)(T) (Section 3.2).
        """
        if not self.are_compatible(first_op.name, second_op.name):
            raise ValueError(f"Incompatible prosodic operations: {first_op.name} and {second_op.name}")

        def composed_transformation(foot: ProsodicFoot) -> ProsodicFoot:
            intermediate = first_op.apply(foot)
            return second_op.apply(intermediate)

        return composed_transformation

    def _initialize_canonical_operators(self) -> None:
        """
        Precompiles standard Zihaf and Illah operators extracted from the
        canonical prosody references (Section 5.1).
        """
        S = SyllableType.SHORT
        L = SyllableType.LONG

        # 1. Khabn: Deletion of second quiescent letter (e.g. Fa'ilun -> Fa'ilun)
        self.register_operator(
            ZihafOperator(
                name="Khabn",
                target_mnemonic="Failun",
                result_mnemonic="Fa'ilun",
                target_syllables=(L, S, L),
                result_syllables=(S, S, L),
                description="Deletion of the second quiescent letter.",
            )
        )
        self.register_operator(
            ZihafOperator(
                name="Khabn_Mustafilun",
                target_mnemonic="Mustaf'ilun",
                result_mnemonic="Muta'filun",
                target_syllables=(L, L, S, L),
                result_syllables=(S, L, S, L),
                description="Khabn applied to Mustaf'ilun -> Mafa'ilun equivalent.",
            )
        )

        # 2. Qabd: Deletion of fifth quiescent letter (e.g. Fa'ulun -> Fa'ulu)
        self.register_operator(
            ZihafOperator(
                name="Qabd",
                target_mnemonic="Fa'ulun",
                result_mnemonic="Fa'ulu",
                target_syllables=(S, L, L),
                result_syllables=(S, L, S),
                description="Deletion of the fifth quiescent letter.",
            )
        )
        self.register_operator(
            ZihafOperator(
                name="Qabd_Mafailun",
                target_mnemonic="Mafa'ilun",
                result_mnemonic="Mafa'ilu",
                target_syllables=(S, L, L, L),
                result_syllables=(S, L, S, L),
                description="Deletion of the fifth quiescent letter from Mafa'ilun.",
            )
        )

        # 3. Idmar: Quiescence of second moving letter (e.g. Mutafa'ilun -> Mutfa'ilun)
        self.register_operator(
            ZihafOperator(
                name="Idmar",
                target_mnemonic="Mutafa'ilun",
                result_mnemonic="Mutfa'ilun",
                target_syllables=(S, S, L, S, L),
                result_syllables=(L, L, S, L),
                description="Quiescence of the second moving consonant in Kamil.",
            )
        )

        # 4. Tayy: Deletion of fourth quiescent letter (e.g. Mustaf'ilun -> Musta'ilun)
        self.register_operator(
            ZihafOperator(
                name="Tayy",
                target_mnemonic="Mustaf'ilun",
                result_mnemonic="Musta'ilun",
                target_syllables=(L, L, S, L),
                result_syllables=(L, S, S, L),
                description="Deletion of the fourth quiescent consonant.",
            )
        )

        # 5. Kaff: Deletion of seventh quiescent letter (e.g. Failatun -> Failatu)
        self.register_operator(
            ZihafOperator(
                name="Kaff",
                target_mnemonic="Fa'ilatun",
                result_mnemonic="Fa'ilatu",
                target_syllables=(L, S, L, L),
                result_syllables=(L, S, L, S),
                description="Deletion of the seventh quiescent letter.",
            )
        )

        # 6. Hadhf (Illah): Deletion of Sabab Khafif from the terminal foot
        self.register_operator(
            IllahOperator(
                name="Hadhf",
                target_mnemonic="Fa'ulun",
                result_mnemonic="Fa'u",
                target_syllables=(S, L, L),
                result_syllables=(S, L),
                terminal_only=True,
                description="Deletion of the final light cord (Sabab Khafif).",
            )
        )

        # 7. Qat' (Illah): Deletion of the sukun of Watad Majmu' and quiescence of the preceding letter
        self.register_operator(
            IllahOperator(
                name="Qat",
                target_mnemonic="Fa'ilun",
                result_mnemonic="Fa'il",
                target_syllables=(L, S, L),
                result_syllables=(L, L),
                terminal_only=True,
                description="Truncation of the final Watad consonant and quiescence of the preceding.",
            )
        )

        # Incompatibility Rules (Section 3.3):
        # E.g., Khabl is composed of Khabn + Tayy, so pure incompatible isolated states are restricted:
        self.register_incompatibility("Idmar", "Waqas")