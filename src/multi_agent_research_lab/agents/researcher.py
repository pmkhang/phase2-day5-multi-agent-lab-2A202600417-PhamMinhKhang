"""Researcher agent implementation."""

from __future__ import annotations

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.search_client import SearchClient


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def __init__(self, search_client: SearchClient | None = None) -> None:
        self.search_client = search_client or SearchClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""

        docs = self.search_client.search(state.request.query, max_results=state.request.max_sources)
        state.sources = docs
        bullets = [f"- {doc.title}: {doc.snippet[:180]}" for doc in docs]
        state.research_notes = "\n".join(bullets) if bullets else "No sources found."
        state.agent_results.append(
            AgentResult(
                agent=AgentName.RESEARCHER,
                content=state.research_notes,
                metadata={"source_count": len(docs)},
            )
        )
        state.add_trace_event("researcher.completed", {"source_count": len(docs)})
        return state
