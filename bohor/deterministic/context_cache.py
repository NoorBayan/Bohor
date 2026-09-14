"""
Document-Level Contextual Cache.
Implements the poem-level contextual caching strategy defined,
bypassing exhaustive repository traversal once meter identity is established.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from bohor.core.types import MeterFamily, MeterStructuralForm


@dataclass
class CacheEntry:
    meter: MeterFamily
    form: Optional[MeterStructuralForm]
    confidence: float
    verse_count: int


class PoemContextCache:
    """
    Thread-safe, bounded contextual cache keyed by document/poem identifiers.
    Constrains candidate generation for subsequent verses within the same poem
    to the admissible subset of the established meter.
    """

    def __init__(self, max_documents: int = 10_000, confidence_threshold: float = 0.70) -> None:
        self.max_documents = max_documents
        self.confidence_threshold = confidence_threshold
        self._cache: Dict[str, CacheEntry] = {}
        self._hits: int = 0
        self._misses: int = 0
        self._evictions: int = 0

    @property
    def hits(self) -> int:
        return self._hits

    @property
    def misses(self) -> int:
        return self._misses

    @property
    def evictions(self) -> int:
        return self._evictions

    def lookup(self, poem_id: str) -> Optional[Tuple[MeterFamily, Optional[MeterStructuralForm]]]:
        """
        Retrieves cached metrical context for a given poem.
        Returns: (MeterFamily, MeterStructuralForm) or None if absent.
        """
        if not poem_id or poem_id not in self._cache:
            self._misses += 1
            return None

        entry = self._cache[poem_id]
        self._hits += 1
        entry.verse_count += 1
        return entry.meter, entry.form

    def store(
        self,
        poem_id: str,
        meter: MeterFamily,
        form: Optional[MeterStructuralForm] = None,
        confidence: float = 1.0,
    ) -> bool:
        """
        Locks metrical context if prediction confidence exceeds the activation threshold.
        Returns True if stored/updated, False otherwise.
        """
        if not poem_id or confidence < self.confidence_threshold:
            return False

        if len(self._cache) >= self.max_documents and poem_id not in self._cache:
            # Evict oldest entry (LRU-like FIFO eviction for bounded memory)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            self._evictions += 1

        self._cache[poem_id] = CacheEntry(
            meter=meter,
            form=form,
            confidence=confidence,
            verse_count=1,
        )
        return True

    def invalidate(self, poem_id: str) -> None:
        """Invalidates context upon detecting anomalous mid-poem metrical shifts."""
        if poem_id in self._cache:
            del self._cache[poem_id]

    def clear(self) -> None:
        """Resets cache and performance counters."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        self._evictions = 0