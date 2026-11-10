# Base state (just messages) passed from START to END; other states extend it so the core loop always works.
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """The state passed between nodes, from START to END."""

    # This reducer appends new messages instead of replacing old ones.
    messages: Annotated[list[BaseMessage], add_messages]
