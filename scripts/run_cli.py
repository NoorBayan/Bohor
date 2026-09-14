"""
Interactive and File-Based Command Line Interface.
Provides unified scansion inspection for single verses and files,
with formatted terminal output and multi-format serialization options.
"""

import argparse
import os
import sys
from typing import List

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bohor.deterministic.repository import PatternRepository
from bohor.pipeline.scansion import ScansionResult, VerseScansionPipeline
from bohor.pipeline.serializer import ScansionSerializer
from bohor.probabilistic.hitl_router import HITLRouter


def format_text_summary(result: ScansionResult) -> str:
    """Formats scansion result into a clear terminal summary."""
    lines: List[str] = [
        "============================================================",
        f"Input Verse:      {result.raw_text}",
        f"Status:           {result.status}",
    ]

    if result.normalized_sadr and result.normalized_ajuz:
        lines.append(f"Normalized Sadr:  {result.normalized_sadr}")
        lines.append(f"Normalized Ajuz:  {result.normalized_ajuz}")
        lines.append(f"Syllable Footprint: {result.footprint}")

    if result.is_success and result.optimal_derivation:
        lines.extend([
            "------------------------------------------------------------",
            f"Detected Meter:   {result.meter.value} ({result.structural_form.value})",
            f"Taf'ilah Sequence: {' | '.join(result.tafilat)}",
            f"Pattern String:   {result.pattern_string}",
            f"Transformations:  {', '.join(result.transformations) if result.transformations else 'Salim'}",
            "------------------------------------------------------------",
            f"Calibrated Prob:  {result.calibrated_probability:.4f}",
            f"Top-Two Margin:   {result.probability_margin:.4f}",
            f"Entropy H(X):     {result.normalized_entropy:.4f}",
            f"Routing Decision: {result.routing_decision.value} (Autonomous: {result.is_autonomous})",
            "------------------------------------------------------------",
            f"Initial Pool:     {result.initial_pool_size} patterns",
            f"Pruned Branches:  {result.pruned_candidates_count} paths",
            f"Surviving Pool:   {result.surviving_candidates_count} candidates",
        ])
    elif result.error_message:
        lines.append(f"Diagnostics:      {result.error_message}")
    else:
        lines.append("Diagnostics:      Rejected by deterministic constraints (Phi(V, M) == 0)")

    lines.append("============================================================")
    return "\n".join(lines)


def run_interactive_mode(pipeline: VerseScansionPipeline) -> None:
    """Runs interactive terminal REPL for continuous verse scansion."""
    sys.stdout.write("Bohor Classical Arabic Prosody Scansion CLI\n")
    sys.stdout.write("Enter verse text (type 'exit' or 'quit' to terminate):\n\n")

    while True:
        try:
            sys.stdout.write("bohor> ")
            sys.stdout.flush()
            line = sys.stdin.readline()
            if not line:
                break
            verse_text = line.strip()
            if not verse_text:
                continue
            if verse_text.lower() in ("exit", "quit", "q"):
                break

            result = pipeline.scan_verse(verse_text)
            sys.stdout.write(format_text_summary(result) + "\n\n")
        except KeyboardInterrupt:
            sys.stdout.write("\nExiting interactive mode.\n")
            break


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Command Line Interface for Bohor Arabic Prosody Analysis."
    )
    parser.add_argument(
        "verse",
        nargs="?",
        type=str,
        help="Poetic verse text to scan (enclose in quotes).",
    )
    parser.add_argument(
        "-i", "--input",
        type=str,
        help="Path to input text file containing verses (one per line).",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Path to output file. Defaults to standard output.",
    )
    parser.add_argument(
        "-r", "--repository",
        type=str,
        default="corpus/Bohor.zip",
        help="Path to Bohor.zip or precompiled CSV pattern repository.",
    )
    parser.add_argument(
        "-f", "--format",
        choices=["summary", "json", "csv", "xml"],
        default="summary",
        help="Output format (summary, json, csv, xml).",
    )
    parser.add_argument(
        "--tau",
        type=float,
        default=HITLRouter.DEFAULT_TAU,
        help=f"Confidence routing threshold (default: {HITLRouter.DEFAULT_TAU}).",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Launch interactive terminal scansion prompt.",
    )
    args = parser.parse_args()

    repo_path = os.path.abspath(args.repository)
    if not os.path.exists(repo_path):
        sys.stderr.write(f"Error: Pattern repository not found at: {repo_path}\n")
        return 1

    # Initialize repository and pipeline
    repo = PatternRepository()
    if repo_path.endswith(".zip"):
        repo.load_from_zip(repo_path)
    else:
        repo.load_from_csv(repo_path)

    router = HITLRouter(tau=args.tau)
    pipeline = VerseScansionPipeline(repository=repo, router=router)

    if args.interactive:
        run_interactive_mode(pipeline)
        return 0

    results: List[ScansionResult] = []

    if args.verse:
        res = pipeline.scan_verse(args.verse)
        results.append(res)
    elif args.input:
        input_path = os.path.abspath(args.input)
        if not os.path.exists(input_path):
            sys.stderr.write(f"Error: Input file not found: {input_path}\n")
            return 1
        with open(input_path, mode="r", encoding="utf-8-sig") as f:
            for idx, line in enumerate(f):
                text = line.strip()
                if text and not text.startswith("#"):
                    res = pipeline.scan_verse(text, verse_id=f"v_{idx+1}")
                    results.append(res)
    else:
        parser.print_help()
        return 1

    # Emit output
    if args.format == "summary":
        output_str = "\n".join(format_text_summary(r) for r in results)
    elif args.format == "json":
        output_str = ScansionSerializer.to_json(results if len(results) > 1 else results[0], indent=2)
    elif args.format == "csv":
        output_str = ScansionSerializer.to_csv(results)
    elif args.format == "xml":
        output_str = ScansionSerializer.to_xml(results if len(results) > 1 else results[0])
    else:
        output_str = ""

    if args.output:
        out_path = os.path.abspath(args.output)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, mode="w", encoding="utf-8") as f:
            f.write(output_str)
        sys.stderr.write(f"Output successfully written to: {out_path}\n")
    else:
        sys.stdout.write(output_str + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
