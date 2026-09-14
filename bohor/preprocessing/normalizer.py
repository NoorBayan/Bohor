# FILE: bohor/preprocessing/normalizer.py
"""
Orthographic and text normalization engine for classical Arabic poetry.
Implements the normalization pipeline specified,
standardizing unicode representations,
handling partial diacritization,
and isolating hemistich boundaries without altering metrical structure.
"""

import re
import unicodedata
from typing import List, Optional, Tuple

from bohor.core.exceptions import TypeIVSearchError


class TextNormalizer:
    """
    Modular, deterministic text normalization pipeline for classical Arabic verses.
    Preserves ortho-phonological markers while removing typographical noise.
    """

    # Unicode codepoints for Arabic diacritics (Harakat and Tanween)
    FATHATAN = "\u064b"
    DAMMATAN = "\u064c"
    KASRATAN = "\u064d"
    FATHA = "\u064e"
    DAMMA = "\u064f"
    KASRA = "\u0650"
    SHADDA = "\u0651"
    SUKUN = "\u0652"
    DAGGER_ALIF = "\u0670"

    ALL_DIACRITICS = {
        FATHATAN,
        DAMMATAN,
        KASRATAN,
        FATHA,
        DAMMA,
        KASRA,
        SHADDA,
        SUKUN,
        DAGGER_ALIF,
    }

    # Standard hemistich delimiters used across classical Arabic poetic corpora
    HEMISTICH_DELIMITERS_REGEX = re.compile(r"(?:\s*[\*\#\/\|]{2,}\s*|\s+[\#\/\|]\s+|\t+|\s{3,})")

    # Characters that are orthographically non-prosodic (punctuation, tatweel, digits)
    TATWEEL = "\u0640"
    EXCLUDED_CHARS_REGEX = re.compile(
        r"[\u0640\d\.\,\:\;\!\?\"\'\(\)\[\]\{\}\<\>\«\»\-\_\=\+\\\@\$\%\^\&\~]"
    )

    # Phonetic expansion of common orthographic abbreviations and implicit long vowels
    IMPLICIT_LONG_VOWELS = {
        "الله": "اللاه",
        "إله": "إلاه",
        "هذا": "هاذا",
        "هذه": "هاذه",
        "هذان": "هاذان",
        "هؤلاء": "هاؤلاء",
        "ذلك": "ذالك",
        "ذلكما": "ذالكما",
        "ذلكم": "ذالكم",
        "كذلك": "كذاالك",
        "لكن": "لاكن",
        "لكنها": "لاكنها",
        "لكنه": "لاكنهو",
        "طه": "طاها",
        "يس": "ياسين",
    }

    def __init__(self, expand_implicit_vowels: bool = True) -> None:
        self.expand_implicit_vowels = expand_implicit_vowels

    def normalize(self, raw_text: str) -> str:
        """
        Executes the end-to-end normalization pipeline on a raw text segment:
        Unicode canonicalization -> Tatweel removal -> Non-prosodic filtering
        -> Orthographic standardization -> Whitespace consolidation.
        """
        if not raw_text or not raw_text.strip():
            return ""

        # Step 1: Unicode Canonical Decomposition & Composition (NFC)
        text = unicodedata.normalize("NFC", raw_text)

        # Step 2: Remove Tatweel (Kashida)
        text = text.replace(self.TATWEEL, "")

        # Step 3: Remove extraneous non-prosodic punctuation and symbols
        text = self.EXCLUDED_CHARS_REGEX.sub(" ", text)

        # Step 4: Standardize Alef variations (Section 4.2)
        # Normalize Wasla, Madda, and variants while preserving the consonant root
        text = re.sub(r"[\u0622\u0623\u0625\u0671]", "\u0627", text)  # آ, أ, إ, ٱ -> ا
        text = text.replace("\u0649", "\u064a")                         # ى -> ي
        text = text.replace("\u0624", "\u0648")                         # ؤ -> و
        text = text.replace("\u0626", "\u064a")                         # ئ -> ي

        # Step 5: Expand orthographically implicit long vowels if enabled
        if self.expand_implicit_vowels:
            words = text.split()
            normalized_words: List[str] = []
            for w in words:
                stripped_w = self.strip_diacritics(w)
                if stripped_w in self.IMPLICIT_LONG_VOWELS:
                    normalized_words.append(self.IMPLICIT_LONG_VOWELS[stripped_w])
                else:
                    normalized_words.append(w)
            text = " ".join(normalized_words)

        # Step 6: Consolidate redundant whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def split_hemistichs(self, verse_text: str) -> Tuple[str, str]:
        """
        Splits a bipartite poetic verse V = <H_left, H_right> (Sadr and Ajuz)
        using corpus delimiter conventions (Section 3.1 & Section 7.1).
        """
        cleaned = verse_text.strip()
        if not cleaned:
            raise TypeIVSearchError(
                message="Cannot segment empty or whitespace-only verse string",
                verse_text=verse_text,
            )

        # Check for standard delimiters: ***, #, /, |, multiple tabs/spaces
        parts = self.HEMISTICH_DELIMITERS_REGEX.split(cleaned)
        if len(parts) >= 2:
            sadr = self.normalize(parts[0])
            ajuz = self.normalize(parts[1])
            if sadr and ajuz:
                return sadr, ajuz

        # Fallback: check for newline separation (two-line verse representation)
        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
        if len(lines) == 2:
            return self.normalize(lines[0]), self.normalize(lines[1])

        # If no explicit delimiter is present, attempt middle-whitespace splitting
        words = cleaned.split()
        if len(words) >= 4:
            midpoint = len(words) // 2
            sadr = self.normalize(" ".join(words[:midpoint]))
            ajuz = self.normalize(" ".join(words[midpoint:]))
            return sadr, ajuz

        # Unsegmentable verse string triggers Type IV search halt
        raise TypeIVSearchError(
            message="Failed to split verse into symmetrical hemistichs (missing standard delimiter)",
            verse_text=verse_text,
        )

    @classmethod
    def strip_diacritics(cls, text: str) -> str:
        """Removes all Arabic Tashkeel diacritics, leaving pure consonantal skeleton."""
        return "".join(ch for ch in text if ch not in cls.ALL_DIACRITICS)

    @classmethod
    def extract_diacritics_mask(cls, text: str) -> List[bool]:
        """Returns boolean mask indicating vocalized character positions."""
        return [ch in cls.ALL_DIACRITICS for ch in text]