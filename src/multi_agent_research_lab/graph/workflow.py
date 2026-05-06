"""Multi-agent workflow implementation."""

from __future__ import annotations

from multi_agent_research_lab.agents import (
    AnalystAgent,
    CriticAgent,
    ResearcherAgent,
    SupervisorAgent,
    WriterAgent,
)
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import flush_trace, trace_span


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph.

    Keep orchestration here; keep agent internals in `agents/`.
    """

    def __init__(self) -> None:
        self.supervisor = SupervisorAgent()
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.writer = WriterAgent()
        self.critic = CriticAgent()

    def build(self) -> dict[str, str]:
        """Return lightweight node map for introspection.

        This starter uses deterministic Python orchestration so the workflow runs
        even without optional langgraph dependencies.
        """

        return {
            "supervisor": "route next step",
            "researcher": "collect sources and notes",
            "analyst": "derive structured insights",
            "writer": "synthesize final answer",
            "critic": "review quality and citation coverage",
            "done": "stop condition",
        }

    def _run_step(self, state: ResearchState, route: str) -> ResearchState:
        with trace_span(
            name=f"agent.{route}",
            attributes={"run_id": state.run_id, "agent": route, "iteration": state.iteration},
        ) as span:
            if route == "researcher":
                state = self.researcher.run(state)
            elif route == "analyst":
                state = self.analyst.run(state)
            elif route == "writer":
                state = self.writer.run(state)
            elif route == "critic":
                state = self.critic.run(state)
            else:
                span["status"] = "error"
                state.errors.append(f"Unknown route: {route}")
                return state

        state.add_trace_event(
            "workflow.step",
            {
                "run_id": state.run_id,
                "agent": route,
                "iteration": state.iteration,
                "status": span["status"],
                "latency_seconds": span["duration_seconds"],
            },
        )
        return state

    def run(self, state: ResearchState) -> ResearchState:
        """Execute workflow and return final state."""

        settings = get_settings()
        _ = self.build()

        while state.iteration < settings.max_iterations:
            state = self.supervisor.run(state)
            route = state.route_history[-1]
            if route == "done":
                break
            state = self._run_step(state, route)
            if state.errors:
                break

        flush_trace(state.run_id, query=state.request.query)
        return state
