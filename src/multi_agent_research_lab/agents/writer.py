"""Writer agent implementation."""

from __future__ import annotations

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""

        source_lines = [f"- {doc.title} ({doc.url or 'local/offline'})" for doc in state.sources]
        user_prompt = (
            f"Query: {state.request.query}\n\n"
            f"Research notes:\n{state.research_notes or 'N/A'}\n\n"
            f"Analysis notes:\n{state.analysis_notes or 'N/A'}\n\n"
            "Write a concise, structured answer. End with 'Sources:' and list each source."
        )
        completion = self.llm_client.complete(
            system_prompt=(
                "You are a technical research writer. Be accurate, concise, and explicit "
                "about uncertainty."
            ),
            user_prompt=user_prompt,
        )

        answer = completion.content.strip()
        if "Sources:" not in answer:
            answer = f"{answer}\n\nSources:\n" + "\n".join(source_lines)

        state.final_answer = answer
        state.agent_results.append(
            AgentResult(
                agent=AgentName.WRITER,
                content=answer,
                metadata={
                    "input_tokens": completion.input_tokens,
                    "output_tokens": completion.output_tokens,
                },
            )
        )
        state.add_trace_event("writer.completed", {"answer_chars": len(answer)})
        return state
