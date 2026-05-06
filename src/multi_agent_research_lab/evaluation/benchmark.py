"""Benchmark skeleton for single-agent vs multi-agent."""

from collections.abc import Callable
from time import perf_counter

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState

Runner = Callable[[str], ResearchState]


def run_benchmark(
    run_name: str, query: str, runner: Runner
) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency and return heuristic benchmark metrics."""

    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started
    writer_result = next(
        (item for item in reversed(state.agent_results) if item.agent == "writer"), None
    )
    input_tokens = None
    output_tokens = None
    if writer_result:
        input_tokens = writer_result.metadata.get("input_tokens")
        output_tokens = writer_result.metadata.get("output_tokens")

    estimated_cost = None
    if isinstance(input_tokens, int) and isinstance(output_tokens, int):
        estimated_cost = ((input_tokens * 0.15) + (output_tokens * 0.60)) / 1_000_000

    source_titles = [doc.title for doc in state.sources if doc.title]
    answer = state.final_answer or ""
    citation_coverage = None
    if source_titles:
        cited = sum(1 for title in source_titles if title in answer)
        citation_coverage = cited / len(source_titles)

    quality = 4.0
    if state.final_answer:
        quality += 2.0
    if state.research_notes:
        quality += 1.5
    if state.analysis_notes:
        quality += 1.5
    if citation_coverage is not None:
        quality += min(citation_coverage, 1.0)
    if state.errors:
        quality -= min(len(state.errors), 3) * 1.5
    quality = max(0.0, min(10.0, quality))

    step_count = max(1, len(state.route_history))
    error_rate = len(state.errors) / step_count
    notes = "heuristic metrics; validate with manual review for final grading"

    metrics = BenchmarkMetrics(
        run_name=run_name,
        latency_seconds=latency,
        estimated_cost_usd=estimated_cost,
        quality_score=quality,
        citation_coverage=citation_coverage,
        error_rate=error_rate,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        notes=notes,
    )
    return state, metrics
