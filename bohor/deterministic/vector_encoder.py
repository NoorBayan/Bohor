# FILE: bohor/deterministic/vector_encoder.py
"""
Vectorized Pattern Encoding Engine.
"""

from typing import Iterable, List, Sequence, Tuple, Union

from bohor.core.types import Syllable, SyllableType


class BitwiseVectorEncoder:
    """
    Encodes prosodic syllable sequences into compact bitwise representations.
    Short syllables (v) -> 0, Long/Overlong syllables (-, ~) -> 1.
    Provides constant-time bitwise operations (XOR, Hamming distance, mask filtering).
    """

    @staticmethod
    def encode_syllables(syllables: Sequence[Union[Syllable, SyllableType]]) -> Tuple[int, int]:
        """
        Converts a sequence of syllables into a packed integer bitmask and its length.
        Returns: (bitmask, bit_length).
        """
        bitmask = 0
        length = len(syllables)
        for s in syllables:
            stype = s.syllable_type if isinstance(s, Syllable) else s
            bitmask = (bitmask << 1) | stype.binary_code
        return bitmask, length

    @staticmethod
    def encode_pattern_string(pattern_str: str) -> Tuple[int, int]:
        """
        Parses standard prosodic notation (e.g. 'v - - v - - -' or '0 1 1 0 1 1 1')
        into an integer bitmask and length.
        """
        tokens = [tok for tok in pattern_str.split() if tok in ("v", "-", "~", "0", "1", "S", "L", "O")]
        if not tokens:
            # Fallback for contiguous unspaced strings like 'v--v---' or '0110111'
            tokens = [ch for ch in pattern_str if ch in ("v", "-", "~", "0", "1", "S", "L", "O")]

        bitmask = 0
        for tok in tokens:
            code = 1 if tok in ("-", "~", "1", "L", "O") else 0
            bitmask = (bitmask << 1) | code
        return bitmask, len(tokens)

    @staticmethod
    def decode_to_syllable_types(bitmask: int, length: int) -> Tuple[SyllableType, ...]:
        """Reconstructs SyllableType sequence from bitmask and length."""
        types: List[SyllableType] = []
        for i in range(length - 1, -1, -1):
            bit = (bitmask >> i) & 1
            types.append(SyllableType.LONG if bit == 1 else SyllableType.SHORT)
        return tuple(types)

    @staticmethod
    def decode_to_arud_string(bitmask: int, length: int) -> str:
        """Reconstructs standard Arud string notation (e.g. 'v - - v - - -')."""
        types = BitwiseVectorEncoder.decode_to_syllable_types(bitmask, length)
        return " ".join(t.arud_symbol for t in types)

    @staticmethod
    def hamming_distance(bitmask1: int, bitmask2: int) -> int:
        """Calculates exact bit differences using bitwise XOR and popcount."""
        return (bitmask1 ^ bitmask2).bit_count()

    @staticmethod
    def matches_prefix(target_mask: int, prefix_mask: int, prefix_len: int, target_len: int) -> bool:
        """
        Determines if target_mask begins with prefix_mask in constant time.
        Used for incremental candidate validation during DAG traversal.
        """
        if prefix_len > target_len:
            return False
        shift = target_len - prefix_len
        aligned_prefix = target_mask >> shift
        return aligned_prefix == prefix_mask