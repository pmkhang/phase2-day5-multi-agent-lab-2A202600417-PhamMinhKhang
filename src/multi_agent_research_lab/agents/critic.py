"""Optional critic agent for post-write quality checks."""

from __future__ import annotations

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState


class CriticAgent(BaseAgent):
    """Optional fact-checking and citation-coverage review."""

    name = "critic"

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append lightweight review findings."""

        findings: list[str] = []
        answer = state.final_answer or ""
        if not answer:
            findings.append("No final answer to review.")
        else:
            if "Sources:" not in answer:
                findings.append("Missing `Sources:` section in final answer.")
            source_titles = [doc.title for doc in state.sources]
            covered_titles = [title for title in source_titles if title and title in answer]
            if source_titles:
                coverage = len(covered_titles) / len(source_titles)
                coverage_text = (
                    f"Citation title coverage: {coverage:.0%} "
                    f"({len(covered_titles)}/{len(source_titles)})."
                )
                findings.append(
                    coverage_text
                )
            else:
                findings.append("No sources available to verify citation coverage.")
            if len(answer.strip()) < 200:
                findings.append("Answer is short; consider adding more context.")

        verdict = "Critic review:\n- " + "\n- ".join(findings)
        state.critic_notes = verdict
        state.agent_results.append(
            AgentResult(
                agent=AgentName.CRITIC,
                content=verdict,
                metadata={"finding_count": len(findings)},
            )
        )
        state.add_trace_event("critic.completed", {"finding_count": len(findings)})
        return state
