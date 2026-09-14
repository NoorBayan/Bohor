"""
High-Throughput Batch Processing Engine.
Embarrassingly parallel corpus-scale execution pipeline described
"""

import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Callable, Iterable, List, Optional, Sequence, Tuple, Union

from bohor.deterministic.repository import PatternRepository
from bohor.pipeline.scansion import ScansionResult, VerseScansionPipeline


# Global worker state for multi-process memory efficiency
_WORKER_PIPELINE: Optional[VerseScansionPipeline] = None


def _init_worker(repository_path: Optional[str], is_zip: bool) -> None:
    """
    Initializes a worker-local VerseScansionPipeline once per process.
    Prevents repeated IPC serialization of the 76,700-pattern repository.
    """
    global _WORKER_PIPELINE
    repo = PatternRepository()
    if repository_path:
        if is_zip or repository_path.endswith(".zip"):
            repo.load_from_zip(repository_path)
        else:
            repo.load_from_csv(repository_path)
    _WORKER_PIPELINE = VerseScansionPipeline(repository=repo)


def _worker_process_single(
    task_payload: Tuple[int, str, Optional[str], Optional[str]],
) -> Tuple[int, ScansionResult]:
    """
    Worker task execution function.
    Returns: (index, ScansionResult) to guarantee input-output ordering preservation.
    """
    global _WORKER_PIPELINE
    idx, raw_text, verse_id, poem_id = task_payload
    if _WORKER_PIPELINE is None:
        raise RuntimeError("Worker process pipeline was not initialized")
    result = _WORKER_PIPELINE.scan_verse(verse_text=raw_text, verse_id=verse_id, poem_id=poem_id)
    return idx, result


@dataclass
class BatchProcessingResult:
    """Aggregated batch execution statistics and structured results."""

    results: List[ScansionResult] = field(default_factory=list)
    total_verses: int = 0
    successful_verses: int = 0
    autonomous_verses: int = 0
    hitl_referred_verses: int = 0
    rejected_verses: int = 0
    total_time_seconds: float = 0.0
    throughput_verses_per_sec: float = 0.0


class BatchProcessor:
    """
    High-performance corpus batch executor.
    Supports single-threaded and multi-core parallel execution across CPU cores,
    maintaining strict deterministic input-to-output ordering.
    """

    def __init__(
        self,
        pipeline: Optional[VerseScansionPipeline] = None,
        repository_path: Optional[str] = None,
        is_zip: bool = False,
    ) -> None:
        self.pipeline = pipeline
        self.repository_path = repository_path
        self.is_zip = is_zip

    def process_batch(
        self,
        verses: Sequence[Union[str, Tuple[str, Optional[str], Optional[str]]]],
        max_workers: int = 1,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> BatchProcessingResult:
        """
        Executes batch processing over input verses:
        - If max_workers <= 1: Executes in sequential mode reusing local pipeline.
        - If max_workers > 1: Dispatches across CPU cores via ProcessPoolExecutor.
        Guarantees exact preservation of input record ordering.
        """
        start_time = time.perf_counter()
        total_count = len(verses)
        if total_count == 0:
            return BatchProcessingResult()

        # Normalize input payloads: (index, text, verse_id, poem_id)
        tasks: List[Tuple[int, str, Optional[str], Optional[str]]] = []
        for idx, item in enumerate(verses):
            if isinstance(item, str):
                tasks.append((idx, item, f"v_{idx}", None))
            elif isinstance(item, tuple) and len(item) == 3:
                tasks.append((idx, item[0], item[1], item[2]))
            else:
                raise ValueError(f"Invalid verse task payload structure at index {idx}: {item}")

        ordered_results: List[Optional[ScansionResult]] = [None] * total_count

        if max_workers <= 1 or self.pipeline is not None and not self.repository_path:
            # Sequential single-process execution path
            active_pipeline = self.pipeline or VerseScansionPipeline(repository=PatternRepository())
            for idx, raw_text, v_id, p_id in tasks:
                res = active_pipeline.scan_verse(verse_text=raw_text, verse_id=v_id, poem_id=p_id)
                ordered_results[idx] = res
                if progress_callback:
                    progress_callback(idx + 1, total_count)
        else:
            # Embarrassingly parallel multi-core execution path (Section 7.4)
            with ProcessPoolExecutor(
                max_workers=max_workers,
                initializer=_init_worker,
                initargs=(self.repository_path, self.is_zip),
            ) as executor:
                future_map = {executor.submit(_worker_process_single, task): task[0] for task in tasks}
                completed_count = 0
                for future in as_completed(future_map):
                    idx, res = future.result()
                    ordered_results[idx] = res
                    completed_count += 1
                    if progress_callback:
                        progress_callback(completed_count, total_count)

        elapsed = time.perf_counter() - start_time
        final_results = [r for r in ordered_results if r is not None]

        # Aggregate batch execution statistics
        success_count = sum(1 for r in final_results if r.is_success)
        autonomous_count = sum(1 for r in final_results if r.is_autonomous)
        hitl_count = sum(1 for r in final_results if r.routing_decision == r.routing_decision.REFERRED_TO_HITL)
        rejected_count = sum(1 for r in final_results if r.status == "REJECTED_OUT_OF_SCOPE")
        throughput = (total_count / elapsed) if elapsed > 0 else 0.0

        return BatchProcessingResult(
            results=final_results,
            total_verses=total_count,
            successful_verses=success_count,
            autonomous_verses=autonomous_count,
            hitl_referred_verses=hitl_count,
            rejected_verses=rejected_count,
            total_time_seconds=round(elapsed, 4),
            throughput_verses_per_sec=round(throughput, 2),
        )