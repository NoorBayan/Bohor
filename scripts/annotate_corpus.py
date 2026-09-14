"""
Silver-Standard Corpus Auto-Annotation Script.
Processes large-scale raw Arabic poetic corpora through the complete scansion pipeline,
enforcing confidence threshold tau=0.70 and recording HITL uncertainty flags.
"""

import argparse
import csv
import os
import sys
import time
from typing import List, Optional, Tuple

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bohor.deterministic.repository import PatternRepository
from bohor.pipeline.batch_processor import BatchProcessor
from bohor.pipeline.scansion import ScansionResult, VerseScansionPipeline
from bohor.pipeline.serializer import ScansionSerializer
from bohor.probabilistic.hitl_router import HITLRouter


def parse_corpus_file(input_path: str) -> List[Tuple[str, Optional[str], Optional[str]]]:
    """
    Parses input corpus file (CSV, TSV, or plaintext).
    Returns list of (verse_text, verse_id, poem_id).
    """
    entries: List[Tuple[str, Optional[str], Optional[str]]] = []
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input corpus file not found: {input_path}")

    _, ext = os.path.splitext(input_path.lower())

    if ext in (".csv", ".tsv"):
        delimiter = "\t" if ext == ".tsv" else ","
        with open(input_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            if reader.fieldnames:
                cols = {name.strip().lower(): name for name in reader.fieldnames}
                text_col = cols.get("verse") or cols.get("text") or cols.get("البيت") or cols.get("raw_text")
                id_col = cols.get("verse_id") or cols.get("id") or cols.get("رقم_البيت")
                poem_col = cols.get("poem_id") or cols.get("قصيدة") or cols.get("poem")

                if text_col:
                    for idx, row in enumerate(reader):
                        text = row[text_col].strip()
                        if text:
                            vid = row[id_col].strip() if id_col and row.get(id_col) else f"v_{idx+1}"
                            pid = row[poem_col].strip() if poem_col and row.get(poem_col) else None
                            entries.append((text, vid, pid))
                    return entries

    # Plaintext fallback: one verse per line
    with open(input_path, mode="r", encoding="utf-8-sig") as f:
        for idx, line in enumerate(f):
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                entries.append((stripped, f"v_{idx+1}", None))

    return entries


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Automated Silver-Standard Corpus Annotation Pipeline (Bohor)."
    )
    parser.add_argument(
        "-i", "--input",
        type=str,
        required=True,
        help="Path to raw corpus file (CSV, TSV, or TXT).",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        required=True,
        help="Path for output annotated corpus file.",
    )
    parser.add_argument(
        "-r", "--repository",
        type=str,
        default="corpus/Bohor.zip",
        help="Path to Bohor.zip or precompiled CSV pattern repository.",
    )
    parser.add_argument(
        "-f", "--format",
        choices=["csv", "json"],
        default="csv",
        help="Output serialization format (csv or json).",
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=1,
        help="Number of parallel CPU worker processes (Section 7.4).",
    )
    parser.add_argument(
        "--tau",
        type=float,
        default=HITLRouter.DEFAULT_TAU,
        help=f"Absolute confidence threshold (default: {HITLRouter.DEFAULT_TAU}).",
    )
    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)
    repo_path = os.path.abspath(args.repository)

    if not os.path.exists(repo_path):
        sys.stderr.write(f"Error: Repository file not found: {repo_path}\n")
        return 1

    sys.stderr.write(f"Loading input corpus from: {input_path}...\n")
    try:
        verse_tasks = parse_corpus_file(input_path)
    except Exception as e:
        sys.stderr.write(f"Error reading corpus file: {str(e)}\n")
        return 1

    total_verses = len(verse_tasks)
    sys.stderr.write(f"Parsed {total_verses} verses for automated scansion.\n")
    if total_verses == 0:
        sys.stderr.write("No valid verses found to annotate.\n")
        return 0

    # Configure repository and batch processor
    is_zip = repo_path.endswith(".zip")
    sys.stderr.write(f"Initializing BatchProcessor (workers={args.workers}, tau={args.tau})...\n")

    if args.workers <= 1:
        repo = PatternRepository()
        if is_zip:
            repo.load_from_zip(repo_path)
        else:
            repo.load_from_csv(repo_path)
        router = HITLRouter(tau=args.tau)
        pipeline = VerseScansionPipeline(repository=repo, router=router)
        processor = BatchProcessor(pipeline=pipeline)
    else:
        processor = BatchProcessor(repository_path=repo_path, is_zip=is_zip)

    last_report_time = time.time()

    def progress_callback(completed: int, total: int) -> None:
        nonlocal last_report_time
        now = time.time()
        if now - last_report_time >= 2.0 or completed == total:
            pct = (completed / total) * 100
            sys.stderr.write(f"\rProgress: {completed}/{total} verses scanned ({pct:.1f}%)...")
            sys.stderr.flush()
            last_report_time = now

    sys.stderr.write("Starting corpus scansion...\n")
    batch_result = processor.process_batch(
        verses=verse_tasks,
        max_workers=args.workers,
        progress_callback=progress_callback,
    )
    sys.stderr.write("\nScansion batch completed.\n")

    # Serialize output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sys.stderr.write(f"Serializing annotations to {output_path} ({args.format.upper()})...\n")

    if args.format == "json":
        json_content = ScansionSerializer.to_json(batch_result.results, indent=2)
        with open(output_path, mode="w", encoding="utf-8") as f:
            f.write(json_content)
    else:
        ScansionSerializer.to_csv(batch_result.results, file_or_buffer=output_path)

    # Print summary diagnostics
    sys.stderr.write("\n=== Annotation Execution Summary ===\n")
    sys.stderr.write(f"Total Verses:            {batch_result.total_verses}\n")
    sys.stderr.write(f"Successfully Scanned:    {batch_result.successful_verses}\n")
    sys.stderr.write(f"Autonomous Annotations:  {batch_result.autonomous_verses} (Confidence >= {args.tau})\n")
    sys.stderr.write(f"HITL-Referred Verses:    {batch_result.hitl_referred_verses}\n")
    sys.stderr.write(f"Deterministic Rejected:  {batch_result.rejected_verses}\n")
    sys.stderr.write(f"Execution Time:          {batch_result.total_time_seconds} seconds\n")
    sys.stderr.write(f"Throughput:              {batch_result.throughput_verses_per_sec} verses/sec\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())