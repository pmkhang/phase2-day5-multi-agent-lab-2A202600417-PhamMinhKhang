"""Benchmark report rendering."""

from multi_agent_research_lab.core.schemas import BenchmarkMetrics


def render_markdown_report(metrics: list[BenchmarkMetrics]) -> str:
    """Render benchmark metrics to markdown."""

    lines = [
        "# Benchmark Report",
        "",
        (
            "| Run | Latency (s) | Cost (USD) | Quality | Citation | "
            "Error rate | Tokens (in/out) | Notes |"
        ),
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for item in metrics:
        cost = "" if item.estimated_cost_usd is None else f"{item.estimated_cost_usd:.4f}"
        quality = "" if item.quality_score is None else f"{item.quality_score:.1f}"
        citation = "" if item.citation_coverage is None else f"{item.citation_coverage * 100:.0f}%"
        error_rate = "" if item.error_rate is None else f"{item.error_rate * 100:.0f}%"
        token_pair = ""
        if item.input_tokens is not None and item.output_tokens is not None:
            token_pair = f"{item.input_tokens}/{item.output_tokens}"
        lines.append(
            "| "
            f"{item.run_name} | {item.latency_seconds:.2f} | {cost} | {quality} | "
            f"{citation} | {error_rate} | {token_pair} | {item.notes} |"
        )

    if len(metrics) >= 2:
        best = max(metrics, key=lambda metric: metric.quality_score or 0)
        fastest = min(metrics, key=lambda metric: metric.latency_seconds)
        lines.extend(
            [
                "",
                "## Highlights",
                f"- Highest quality: **{best.run_name}** ({(best.quality_score or 0):.1f}/10)",
                f"- Fastest: **{fastest.run_name}** ({fastest.latency_seconds:.2f}s)",
            ]
        )
    return "\n".join(lines) + "\n"
