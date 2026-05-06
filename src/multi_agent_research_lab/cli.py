"""Command-line entrypoint for the lab starter."""

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.evaluation.benchmark import run_benchmark
from multi_agent_research_lab.evaluation.report import render_markdown_report
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.storage import LocalArtifactStore

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


def _run_baseline_state(query: str) -> ResearchState:
    request = ResearchQuery(query=query)
    llm = LLMClient()
    completion = llm.complete(
        system_prompt=(
            "You are a single-agent research assistant. Provide a concise answer and "
            "state assumptions when evidence is limited."
        ),
        user_prompt=f"Research and answer this query:\n\n{request.query}",
    )
    state = ResearchState(request=request)
    state.final_answer = completion.content
    return state


def _run_multi_agent_state(query: str) -> ResearchState:
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    return workflow.run(state)


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a minimal single-agent baseline."""

    _init()
    state = _run_baseline_state(query)
    console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline"))


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow."""

    _init()
    result = _run_multi_agent_state(query)
    console.print(result.model_dump_json(indent=2))


@app.command()
def benchmark(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Compare single-agent baseline vs multi-agent workflow and save a report."""

    _init()
    _, baseline_metrics = run_benchmark("single-agent", query, _run_baseline_state)
    _, multi_metrics = run_benchmark("multi-agent", query, _run_multi_agent_state)
    report = render_markdown_report([baseline_metrics, multi_metrics])

    store = LocalArtifactStore()
    report_path = store.write_text("benchmark_report.md", report)
    console.print(Panel.fit(report, title="Benchmark Summary"))
    console.print(f"Saved report to: {report_path}")


if __name__ == "__main__":
    app()
