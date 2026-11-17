# Creates the Claude model bound to a tool list, so each workflow gets a model with only its own tools.
from langchain_anthropic import ChatAnthropic

from app.core.config import settings


def make_model(tools: list, model_name: str | None = None, max_tokens: int = 16384):
    """Create a Claude chat model that knows which tools it can call."""
    return ChatAnthropic(
        model=model_name or settings.default_model,
        api_key=settings.anthropic_api_key or None,  # None = fall back to the ANTHROPIC_API_KEY env var
        max_tokens=max_tokens,
    ).bind_tools(tools)
