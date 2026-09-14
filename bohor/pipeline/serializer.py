"""
Structured Scansion Serializer.
multi-format serialization (JSON, CSV, XML) for scansion results,
preserving complete derivational structures and statistical metadata
"""

import csv
import io
import json
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Sequence, TextIO, Union

from bohor.pipeline.scansion import ScansionResult


class ScansionSerializer:
    """
    Serializes individual and batched ScansionResult objects into stable JSON,
    tabular CSV, and hierarchical XML schemas.
    """

    @classmethod
    def to_dict(cls, result: ScansionResult) -> Dict[str, Any]:
        """Converts a ScansionResult into a structured Python dictionary."""
        return {
            "verse_id": result.verse_id,
            "poem_id": result.poem_id,
            "raw_text": result.raw_text,
            "status": result.status,
            "normalized": {
                "sadr": result.normalized_sadr,
                "ajuz": result.normalized_ajuz,
                "footprint": result.footprint,
            },
            "derivation": {
                "meter": result.meter.value if result.meter else None,
                "structural_form": result.structural_form.value if result.structural_form else None,
                "tafilat": list(result.tafilat),
                "transformations": list(result.transformations),
                "pattern_string": result.pattern_string,
            }
            if result.optimal_derivation
            else None,
            "statistical_metrics": {
                "raw_score": result.raw_score,
                "calibrated_probability": result.calibrated_probability,
                "probability_margin": result.probability_margin,
                "normalized_entropy": result.normalized_entropy,
                "features": result.features,
            },
            "routing": {
                "decision": result.routing_decision.value,
                "is_autonomous": result.is_autonomous,
            },
            "diagnostics": {
                "initial_pool_size": result.initial_pool_size,
                "pruned_candidates": result.pruned_candidates_count,
                "surviving_candidates": result.surviving_candidates_count,
                "dag_nodes": result.dag_nodes_count,
                "error_message": result.error_message,
            },
        }

    @classmethod
    def to_json(
        cls,
        results: Union[ScansionResult, Sequence[ScansionResult]],
        indent: Optional[int] = 2,
    ) -> str:
        """Serializes one or more ScansionResult instances to a JSON string."""
        if isinstance(results, ScansionResult):
            payload = cls.to_dict(results)
        else:
            payload = [cls.to_dict(r) for r in results]
        return json.dumps(payload, ensure_ascii=False, indent=indent)

    @classmethod
    def to_csv_records(cls, results: Sequence[ScansionResult]) -> List[Dict[str, Any]]:
        """Converts results to flat, tabular records suitable for CSV serialization."""
        records: List[Dict[str, Any]] = []
        for r in results:
            rec = {
                "verse_id": r.verse_id or "",
                "poem_id": r.poem_id or "",
                "status": r.status,
                "meter": r.meter.value if r.meter else "",
                "structural_form": r.structural_form.value if r.structural_form else "",
                "pattern_string": r.pattern_string,
                "tafilat": " ".join(r.tafilat),
                "transformations": ", ".join(r.transformations),
                "calibrated_probability": r.calibrated_probability,
                "probability_margin": r.probability_margin,
                "normalized_entropy": r.normalized_entropy,
                "routing_decision": r.routing_decision.value,
                "is_autonomous": r.is_autonomous,
                "initial_pool_size": r.initial_pool_size,
                "surviving_candidates": r.surviving_candidates_count,
                "raw_text": r.raw_text,
            }
            records.append(rec)
        return records

    @classmethod
    def to_csv(
        cls,
        results: Sequence[ScansionResult],
        file_or_buffer: Optional[Union[str, TextIO]] = None,
    ) -> str:
        """
        Serializes results into a standardized CSV format. Writes to file if path/stream
        provided; returns CSV string otherwise.
        """
        records = cls.to_csv_records(results)
        if not records:
            header = [
                "verse_id", "poem_id", "status", "meter", "structural_form",
                "pattern_string", "tafilat", "transformations", "calibrated_probability",
                "probability_margin", "normalized_entropy", "routing_decision",
                "is_autonomous", "initial_pool_size", "surviving_candidates", "raw_text",
            ]
            string_io = io.StringIO()
            writer = csv.DictWriter(string_io, fieldnames=header)
            writer.writeheader()
            return string_io.getvalue()

        fieldnames = list(records[0].keys())

        if isinstance(file_or_buffer, str):
            with open(file_or_buffer, mode="w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(records)
            return ""
        elif file_or_buffer is not None:
            writer = csv.DictWriter(file_or_buffer, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
            return ""
        else:
            string_io = io.StringIO()
            writer = csv.DictWriter(string_io, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
            return string_io.getvalue()

    @classmethod
    def to_xml(
        cls,
        results: Union[ScansionResult, Sequence[ScansionResult]],
    ) -> str:
        """Serializes results into well-formed XML preserving hierarchical derivations."""
        root = ET.Element("bohor_scansion_output")
        items = [results] if isinstance(results, ScansionResult) else results

        for r in items:
            verse_elem = ET.SubElement(root, "verse")
            if r.verse_id:
                verse_elem.set("id", str(r.verse_id))
            if r.poem_id:
                verse_elem.set("poem_id", str(r.poem_id))
            verse_elem.set("status", r.status)

            raw_text_elem = ET.SubElement(verse_elem, "raw_text")
            raw_text_elem.text = r.raw_text

            if r.optimal_derivation:
                deriv_elem = ET.SubElement(verse_elem, "derivation")
                meter_elem = ET.SubElement(deriv_elem, "meter")
                meter_elem.text = r.meter.value if r.meter else ""
                form_elem = ET.SubElement(deriv_elem, "form")
                form_elem.text = r.structural_form.value if r.structural_form else ""
                pat_elem = ET.SubElement(deriv_elem, "pattern")
                pat_elem.text = r.pattern_string

                tafilat_elem = ET.SubElement(deriv_elem, "tafilat")
                for taf in r.tafilat:
                    t_item = ET.SubElement(tafilat_elem, "tafilah")
                    t_item.text = taf

                trans_elem = ET.SubElement(deriv_elem, "transformations")
                for tr in r.transformations:
                    tr_item = ET.SubElement(trans_elem, "transformation")
                    tr_item.text = tr

            metrics_elem = ET.SubElement(verse_elem, "metrics")
            ET.SubElement(metrics_elem, "calibrated_probability").text = str(r.calibrated_probability)
            ET.SubElement(metrics_elem, "probability_margin").text = str(r.probability_margin)
            ET.SubElement(metrics_elem, "normalized_entropy").text = str(r.normalized_entropy)

            routing_elem = ET.SubElement(verse_elem, "routing")
            routing_elem.set("decision", r.routing_decision.value)
            routing_elem.set("is_autonomous", str(r.is_autonomous))

        # Decode as pretty-formatted string
        return ET.tostring(root, encoding="utf-8").decode("utf-8")