"""Search client abstraction for ResearcherAgent."""

from __future__ import annotations

import json
from urllib import request

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import SourceDocument


class SearchClient:
    """Provider-agnostic search client with Tavily + offline fallback."""

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query."""

        settings = get_settings()
        if settings.tavily_api_key:
            try:
                payload = json.dumps(
                    {
                        "query": query,
                        "max_results": max_results,
                        "search_depth": "basic",
                        "topic": "general",
                    }
                ).encode("utf-8")
                req = request.Request(
                    url="https://api.tavily.com/search",
                    data=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {settings.tavily_api_key}",
                    },
                    method="POST",
                )
                with request.urlopen(req, timeout=20) as resp:  # nosec B310
                    body = json.loads(resp.read().decode("utf-8"))
                results = body.get("results", [])
                docs = [
                    SourceDocument(
                        title=item.get("title", "Untitled"),
                        url=item.get("url"),
                        snippet=item.get("content", "")[:500],
                        metadata={"score": item.get("score")},
                    )
                    for item in results[:max_results]
                ]
                if docs:
                    return docs
            except Exception:
                pass

        # Offline fallback keeps the workflow functional for local labs.
        return [
            SourceDocument(
                title="Fallback Source 1",
                url=None,
                snippet=(
                    f"Background notes for query '{query}'. "
                    "Multi-agent systems split planning, retrieval, analysis, and writing "
                    "to improve controllability and traceability."
                ),
                metadata={"source": "offline"},
            ),
            SourceDocument(
                title="Fallback Source 2",
                url=None,
                snippet=(
                    "Common trade-offs: better decomposition quality versus higher latency "
                    "and orchestration complexity compared with single-agent baselines."
                ),
                metadata={"source": "offline"},
            ),
        ][:max_results]
