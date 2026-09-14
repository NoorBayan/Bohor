"""
Morpho-phonological syllabification and prosodic transcription engine.
"""

import re
from typing import List, Optional, Tuple

from bohor.core.exceptions import TypeIVSearchError
from bohor.core.types import Hemistich, ProsodicFoot, Syllable, SyllableType, Verse
from bohor.preprocessing.normalizer import TextNormalizer


class ProsodicSyllabifier:
    """
    Implements classical Arud phonological transcription and syllabification:
    Written form -> Phonetic realization -> Metric Syllables (Section 3.1 & 4.2).
    Generates deterministic skeletal footprints for constant-time repository lookup.
    """

    # Solar consonants causing complete assimilation of Lam in 'Al-' (Al-Huruf Al-Shamsiyyah)
    SOLAR_CONSONANTS = {
        "ت", "ث", "د", "ذ", "ر", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ل", "ن"
    }

    # Weak long vowel consonants (Huruf Al-Madd)
    LONG_VOWEL_LETTERS = {"ا", "و", "ي"}

    def __init__(self, normalizer: Optional[TextNormalizer] = None) -> None:
        self.normalizer = normalizer or TextNormalizer()

    def phonetize(self, text: str, is_terminal_hemistich: bool = False) -> str:
        """
        Converts normalized orthography into phonetic Arud transcription
        ('Al-Kitabah Al-Arudiyyah'), encoding phonetic segments:
        - Nunation (Tanween) becomes explicit consonant Nun with Sukun (نْ).
        - Gemination (Shadda) decomposes into consonant_sukun + consonant_vowel.
        - Solar Lam assimilates; silent Wasla elides in continuous phonation.
        - End-of-hemistich vowel elongation (Ishba') is applied if terminal.
        """
        if not text.strip():
            return ""

        words = text.strip().split()
        phonetic_words: List[str] = []

        for idx, word in enumerate(words):
            p_word = word

            # 1. Expand Tanween to Vowel + Sukun Nun
            p_word = p_word.replace(TextNormalizer.FATHATAN, TextNormalizer.FATHA + "ن" + TextNormalizer.SUKUN)
            p_word = p_word.replace(TextNormalizer.DAMMATAN, TextNormalizer.DAMMA + "ن" + TextNormalizer.SUKUN)
            p_word = p_word.replace(TextNormalizer.KASRATAN, TextNormalizer.KASRA + "ن" + TextNormalizer.SUKUN)

            # 2. Expand Shadda (Gemination: Cّ -> Cْ + C)
            expanded_shadda: List[str] = []
            chars = list(p_word)
            i = 0
            while i < len(chars):
                if i + 1 < len(chars) and chars[i + 1] == TextNormalizer.SHADDA:
                    cons = chars[i]
                    vowel = chars[i + 2] if (i + 2 < len(chars) and chars[i + 2] in TextNormalizer.ALL_DIACRITICS) else ""
                    expanded_shadda.extend([cons, TextNormalizer.SUKUN, cons])
                    if vowel:
                        expanded_shadda.append(vowel)
                        i += 3
                    else:
                        i += 2
                else:
                    expanded_shadda.append(chars[i])
                    i += 1
            p_word = "".join(expanded_shadda)

            # 3. Handle Definite Article 'Al-' (Assimilation & Elision)
            stripped_word = self.normalizer.strip_diacritics(p_word)
            if stripped_word.startswith("ال") and len(stripped_word) > 2:
                third_letter = stripped_word[2]
                if third_letter in self.SOLAR_CONSONANTS:
                    # Solar assimilation: replace 'ال' with consonant gemination
                    if idx > 0:
                        # Non-initial word: Hamzat Al-Wasl and Lam are completely dropped
                        p_word = p_word[2:]
                    else:
                        # Initial word: Hamzat Al-Wasl remains vocalized, Lam assimilates
                        p_word = "ا" + TextNormalizer.FATHA + p_word[2:]
                else:
                    # Lunar: Wasla elides if preceded by phonation
                    if idx > 0 and p_word.startswith("ال"):
                        p_word = "ل" + TextNormalizer.SUKUN + p_word[2:]

            phonetic_words.append(p_word)

        phonetic_line = " ".join(phonetic_words)

        # 4. Apply Ishba' (Metrical Elongation) to terminal vowel of hemistich
        if is_terminal_hemistich and phonetic_line:
            last_char = phonetic_line[-1]
            if last_char == TextNormalizer.FATHA:
                phonetic_line += "ا"
            elif last_char == TextNormalizer.DAMMA:
                phonetic_line += "و"
            elif last_char == TextNormalizer.KASRA:
                phonetic_line += "ي"

        return phonetic_line

    def syllabify(self, phonetic_or_raw_text: str) -> List[Syllable]:
        """
        Segments phonetically processed text into atomic metric Syllable objects:
        - Short (S): Single moving consonant (Mutaharrik) [v]
        - Long (L): Moving consonant + Quiescent (Sabab Khafif / Long Vowel) [-]
        - Overlong (O): Syllable with surplus coda at cadence [~]
        """
        text = phonetic_or_raw_text.strip()
        if not text:
            return []

        # Remove spaces to form contiguous phonological utterance
        chars = [ch for ch in text if not ch.isspace()]
        syllables: List[Syllable] = []

        i = 0
        n = len(chars)
        while i < n:
            curr_char = chars[i]
            # Skip floating diacritics if encountered isolated
            if curr_char in TextNormalizer.ALL_DIACRITICS:
                i += 1
                continue

            # Check for vowel or sukun following the current consonant
            has_diacritic = (i + 1 < n) and (chars[i + 1] in TextNormalizer.ALL_DIACRITICS)
            diacritic = chars[i + 1] if has_diacritic else ""
            step = 2 if has_diacritic else 1

            # Look ahead to determine if a quiescent letter (Sukun or Harf Madd) follows
            is_followed_by_quiescent = False
            next_idx = i + step
            if next_idx < n:
                next_char = chars[next_idx]
                if next_char == TextNormalizer.SUKUN:
                    is_followed_by_quiescent = True
                    step += 1
                elif next_char in self.LONG_VOWEL_LETTERS:
                    # Long vowel functions as quiescent Sabab coda
                    is_followed_by_quiescent = True
                    step += 1

            if is_followed_by_quiescent:
                # Long Syllable (L): 2 morae (Sabab Khafif / Watad segment)
                segment = "".join(chars[i : i + step])
                syllables.append(Syllable(phonetic_text=segment, syllable_type=SyllableType.LONG))
            else:
                # Short Syllable (S): 1 mora (Mutaharrik)
                segment = "".join(chars[i : i + step])
                syllables.append(Syllable(phonetic_text=segment, syllable_type=SyllableType.SHORT))

            i += step

        return syllables

    def extract_unvocalized_syllables(self, verse_text: str) -> str:
        """
        Algorithm 1, Phase 1: ExtractUnvocalizedSyllables(V)
        Produces the deterministic skeletal footprint from unvocalized/partially
        vocalized verse text to query the indexed pattern repository.
        Consonant and long vowel skeletal configurations are mapped to standard
        prosodic length footprints (e.g. 'v - - v - - -').
        """
        normalized = self.normalizer.normalize(verse_text)
        stripped = self.normalizer.strip_diacritics(normalized)

        if not stripped:
            raise TypeIVSearchError(
                message="Cannot extract footprint from text lacking consonantal content",
                verse_text=verse_text,
            )

        # Build skeletal footprint based on consonantal intervals and long vowels
        footprint_tokens: List[str] = []
        words = stripped.split()
        for w in words:
            j = 0
            m = len(w)
            while j < m:
                ch = w[j]
                if ch in self.LONG_VOWEL_LETTERS and j > 0:
                    footprint_tokens.append(SyllableType.LONG.arud_symbol)
                else:
                    # Next letter is long vowel -> will form a long syllable
                    if (j + 1 < m) and (w[j + 1] in self.LONG_VOWEL_LETTERS):
                        footprint_tokens.append(SyllableType.LONG.arud_symbol)
                        j += 1
                    else:
                        footprint_tokens.append(SyllableType.SHORT.arud_symbol)
                j += 1

        return " ".join(footprint_tokens)

    def process_verse_into_units(
        self,
        raw_verse: str,
        verse_id: Optional[str] = None,
        poet: Optional[str] = None,
        era: Optional[str] = None,
    ) -> Tuple[Verse, str]:
        """
        End-to-end preprocessing helper: parses raw verse into structured
        core.types.Verse and extracts its skeletal footprint for Algorithm 1.
        """
        sadr_raw, ajuz_raw = self.normalizer.split_hemistichs(raw_verse)

        sadr_phonetic = self.phonetize(sadr_raw, is_terminal_hemistich=True)
        ajuz_phonetic = self.phonetize(ajuz_raw, is_terminal_hemistich=True)

        sadr_syllables = tuple(self.syllabify(sadr_phonetic))
        ajuz_syllables = tuple(self.syllabify(ajuz_phonetic))

        # Encapsulate as atomic hemistichs
        sadr_hemistich = Hemistich(feet=(), raw_text=sadr_raw)
        ajuz_hemistich = Hemistich(feet=(), raw_text=ajuz_raw)

        verse_obj = Verse(
            first_hemistich=sadr_hemistich,
            second_hemistich=ajuz_hemistich,
            verse_id=verse_id,
            poet=poet,
            era=era,
        )

        full_footprint = self.extract_unvocalized_syllables(raw_verse)
        return verse_obj, full_footprint