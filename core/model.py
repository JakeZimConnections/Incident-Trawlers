# Creates the Claude model bound to a tool list, so each workflow gets a model with only its own tools.
from langchain_anthropic import ChatAnthropic

DEFAULT_MODEL = "claude-sonnet-4-6"


def make_model(tools: list, model_name: str = DEFAULT_MODEL, max_tokens: int = 16384):
    """Create a Claude chat model that knows which tools it can call."""
    return ChatAnthropic(model=model_name, max_tokens=max_tokens).bind_tools(tools)
