"""Analyst agent implementation."""

from __future__ import annotations

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""

        if not state.research_notes:
            state.analysis_notes = "No research notes available for analysis."
        else:
            source_titles = [doc.title for doc in state.sources]
            state.analysis_notes = (
                "Key findings:\n"
                f"- Retrieved {len(state.sources)} sources\n"
                f"- Main themes inferred from notes and snippets\n"
                "Risks / caveats:\n"
                "- Potential source bias\n"
                "- Requires citation verification for critical claims\n"
                f"Source titles: {', '.join(source_titles)}"
            )

        state.agent_results.append(
            AgentResult(agent=AgentName.ANALYST, content=state.analysis_notes)
        )
        state.add_trace_event("analyst.completed", {"has_analysis": bool(state.analysis_notes)})
        return state
