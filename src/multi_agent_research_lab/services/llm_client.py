"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

from __future__ import annotations

from dataclasses import dataclass

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import AgentExecutionError


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client with OpenAI implementation and safe fallback."""

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion.

        Uses OpenAI when API key is configured; otherwise returns a deterministic
        fallback response so the lab can run end-to-end in offline mode.
        """

        settings = get_settings()
        if not settings.openai_api_key:
            return LLMResponse(content=(f"[offline-fallback] {user_prompt[:600]}"))

        try:
            from openai import OpenAI

            client = OpenAI(api_key=settings.openai_api_key)
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            content = ""
            choices = getattr(response, "choices", None) or []
            if choices:
                first_choice = choices[0]
                message = getattr(first_choice, "message", None)
                content = getattr(message, "content", "") or ""

            input_tokens: int | None = None
            output_tokens: int | None = None
            usage = getattr(response, "usage", None)
            if usage is not None:
                input_tokens = getattr(usage, "prompt_tokens", None)
                output_tokens = getattr(usage, "completion_tokens", None)

            return LLMResponse(
                content=content.strip() or "(empty response)",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
        except Exception as exc:  # pragma: no cover - network/provider variability
            raise AgentExecutionError(f"LLM completion failed: {exc}") from exc
