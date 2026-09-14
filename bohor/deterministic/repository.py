# FILE: bohor/deterministic/repository.py
"""
Indexed Metrical Repository Engine.
Manages the finite database of 76,700 mathematically admissible metrical configurations,
"""

import csv
import io
import os
import zipfile
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from bohor.core.exceptions import RepositoryFormatError
from bohor.core.types import (
    Derivation,
    MeterFamily,
    MeterStructuralForm,
    ProsodicFoot,
    SyllableType,
)
from bohor.deterministic.vector_encoder import BitwiseVectorEncoder


@dataclass(frozen=True)
class PatternRecord:
    """
    Lightweight immutable entity representing a single precompiled prosodic pattern.
    Avoids runtime allocation overhead by functioning as a persistent database pointer.
    """

    pattern_id: int
    meter: MeterFamily
    form: MeterStructuralForm
    pattern_string: str
    bitmask: int
    length: int
    tafilat: Tuple[str, ...]
    transformations: Tuple[str, ...]

    def to_derivation(self) -> Derivation:
        """Converts database record to structured Derivation domain object."""
        decoded_types = BitwiseVectorEncoder.decode_to_syllable_types(self.bitmask, self.length)
        
        # Partition syllables across Taf'ilah mnemonics proportionally
        feet_list: List[ProsodicFoot] = []
        avg_foot_len = max(1, len(decoded_types) // max(1, len(self.tafilat)))
        
        for idx, mnem in enumerate(self.tafilat):
            start = idx * avg_foot_len
            end = len(decoded_types) if idx == len(self.tafilat) - 1 else (idx + 1) * avg_foot_len
            foot_sylls = decoded_types[start:end]
            feet_list.append(
                ProsodicFoot(
                    mnemonic=mnem,
                    syllables=foot_sylls,
                    transformations=self.transformations if idx == len(self.tafilat) - 1 else (),
                )
            )

        return Derivation(
            meter=self.meter,
            form=self.form,
            feet_sequence=tuple(feet_list),
            transformations=self.transformations,
            pattern_string=self.pattern_string,
            binary_vector=tuple(int((self.bitmask >> i) & 1) for i in range(self.length - 1, -1, -1)),
        )


class PatternRepository:
    """
    In-memory indexed database storing all 76,700 admissible classical metrical configurations.
    Maintains primary hash index by syllable footprint, bitmask indexes, and secondary meter indexes.
    """

    def __init__(self) -> None:
        self._records: List[PatternRecord] = []
        self._footprint_index: Dict[str, List[PatternRecord]] = {}
        self._bitmask_index: Dict[Tuple[int, int], List[PatternRecord]] = {}
        self._meter_index: Dict[MeterFamily, List[PatternRecord]] = {}
        self._form_index: Dict[Tuple[MeterFamily, MeterStructuralForm], List[PatternRecord]] = {}
        self._is_loaded: bool = False

    @property
    def total_patterns(self) -> int:
        return len(self._records)

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    def load_from_csv(self, file_path_or_buffer: Union[str, io.TextIOBase]) -> None:
        """
        Loads repository records from a CSV file or buffer, establishing primary
        and secondary lookup indices. Auto-detects column headers.
        """
        self.clear()

        if isinstance(file_path_or_buffer, str):
            if not os.path.exists(file_path_or_buffer):
                raise RepositoryFormatError(f"Pattern repository file not found: {file_path_or_buffer}")
            with open(file_path_or_buffer, mode="r", encoding="utf-8-sig") as f:
                self._parse_csv_content(f)
        else:
            self._parse_csv_content(file_path_or_buffer)

        self._is_loaded = True

    def load_from_zip(self, zip_path: str, inner_csv_name: Optional[str] = None) -> None:
        """Loads repository directly from Bohor.zip archive without requiring manual extraction."""
        if not os.path.exists(zip_path):
            raise RepositoryFormatError(f"Zip archive not found: {zip_path}")

        try:
            with zipfile.ZipFile(zip_path, "r") as z:
                csv_files = [name for name in z.namelist() if name.endswith(".csv") and not name.startswith("__MACOSX")]
                if not csv_files:
                    raise RepositoryFormatError(f"No CSV file found inside archive: {zip_path}")
                
                target_file = inner_csv_name if inner_csv_name in csv_files else csv_files[0]
                with z.open(target_file, "r") as byte_file:
                    text_buffer = io.TextIOWrapper(byte_file, encoding="utf-8-sig")
                    self._parse_csv_content(text_buffer)
        except zipfile.BadZipFile as e:
            raise RepositoryFormatError(f"Corrupted or invalid zip file {zip_path}: {str(e)}")

        self._is_loaded = True

    def _parse_csv_content(self, text_stream: io.TextIOBase) -> None:
        """Parses CSV stream, resolving schema differences and building indices."""
        reader = csv.DictReader(text_stream)
        if not reader.fieldnames:
            raise RepositoryFormatError("Pattern repository CSV lacks header row")

        # Schema column normalization
        cols = {name.strip().lower(): name for name in reader.fieldnames}
        
        meter_col = cols.get("meter") or cols.get("bahr") or cols.get("البحر") or cols.get("meter_name")
        pattern_col = cols.get("pattern") or cols.get("arud_pattern") or cols.get("النمط") or cols.get("syllables")
        form_col = cols.get("form") or cols.get("type") or cols.get("النوع") or cols.get("structural_form")
        feet_col = cols.get("feet") or cols.get("tafilat") or cols.get("التفاعيل") or cols.get("tafilah_sequence")
        trans_col = cols.get("transformations") or cols.get("zihaf_illah") or cols.get("الزحافات_والعلل")
        id_col = cols.get("id") or cols.get("pattern_id") or cols.get("index")

        if not meter_col or not pattern_col:
            raise RepositoryFormatError(
                f"Required columns (meter, pattern) missing in repository schema. Available: {reader.fieldnames}"
            )

        record_id = 1
        for row in reader:
            raw_meter = row[meter_col].strip()
            raw_pattern = row[pattern_col].strip()
            raw_form = row[form_col].strip() if form_col and row.get(form_col) else "Tam"
            raw_feet = row[feet_col].strip() if feet_col and row.get(feet_col) else ""
            raw_trans = row[trans_col].strip() if trans_col and row.get(trans_col) else ""

            try:
                meter_enum = MeterFamily.from_arabic_name(raw_meter)
            except ValueError:
                continue

            form_enum = MeterStructuralForm.MUJZU if ("مجزوء" in raw_form or "mujzu" in raw_form.lower()) else MeterStructuralForm.TAM
            bitmask, length = BitwiseVectorEncoder.encode_pattern_string(raw_pattern)
            normalized_pattern = BitwiseVectorEncoder.decode_to_arud_string(bitmask, length)

            tafilat_tuple = tuple(raw_feet.split()) if raw_feet else ()
            trans_tuple = tuple(t.strip() for t in raw_trans.split(",")) if raw_trans else ()

            pid = int(row[id_col]) if id_col and row.get(id_col) and row[id_col].isdigit() else record_id
            record_id += 1

            rec = PatternRecord(
                pattern_id=pid,
                meter=meter_enum,
                form=form_enum,
                pattern_string=normalized_pattern,
                bitmask=bitmask,
                length=length,
                tafilat=tafilat_tuple,
                transformations=trans_tuple,
            )

            self._records.append(rec)
            self._index_record(rec)

    def _index_record(self, record: PatternRecord) -> None:
        """Stores record in primary and secondary hash indices."""
        # 1. Primary Footprint Index (normalized pattern string)
        if record.pattern_string not in self._footprint_index:
            self._footprint_index[record.pattern_string] = []
        self._footprint_index[record.pattern_string].append(record)

        # 2. Binary Signature Index
        key = (record.bitmask, record.length)
        if key not in self._bitmask_index:
            self._bitmask_index[key] = []
        self._bitmask_index[key].append(record)

        # 3. Meter Family Index (Secondary)
        if record.meter not in self._meter_index:
            self._meter_index[record.meter] = []
        self._meter_index[record.meter].append(record)

        # 4. Structural Form Index (Secondary)
        form_key = (record.meter, record.form)
        if form_key not in self._form_index:
            self._form_index[form_key] = []
        self._form_index[form_key].append(record)

    def query_by_footprint(self, footprint_key: str) -> List[PatternRecord]:
        """Algorithm 1, Phase 1: QueryRepository(M, key=Footprint) in expected O(1) time."""
        normalized_key = " ".join(tok for tok in footprint_key.split() if tok in ("v", "-", "~"))
        return self._footprint_index.get(normalized_key, [])

    def query_by_bitmask(self, bitmask: int, length: int) -> List[PatternRecord]:
        """Bitwise indexed retrieval matching binary vector signatures."""
        return self._bitmask_index.get((bitmask, length), [])

    def query_by_meter(self, meter: MeterFamily) -> List[PatternRecord]:
        """Retrieves admissible subset restricted to a specific meter (used in contextual caching)."""
        return self._meter_index.get(meter, [])

    def query_by_meter_and_form(self, meter: MeterFamily, form: MeterStructuralForm) -> List[PatternRecord]:
        """Retrieves admissible subset restricted to meter and structural form (Tam / Mujzu')."""
        return self._form_index.get((meter, form), [])

    def clear(self) -> None:
        """Clears all records and indexed hash maps."""
        self._records.clear()
        self._footprint_index.clear()
        self._bitmask_index.clear()
        self._meter_index.clear()
        self._form_index.clear()
        self._is_loaded = False