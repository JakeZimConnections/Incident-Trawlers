# Graph state schemas workflows choose from; every one extends AgentState so the shared loop always finds messages.
import operator
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """The state passed between nodes, from START to END."""

    # This reducer appends new messages instead of replacing old ones.
    messages: Annotated[list[BaseMessage], add_messages]


class ZimState(AgentState):
    """AgentState plus the evidence gathered while investigating a ZIM incident."""

    # The user's Cognito details (e.g. sub, email, status). Overwritten.
    cognito_user: dict | None

    # The Stripe payment reference (e.g. a payment intent ID). Overwritten.
    stripe_ref: str | None

    # Log lines pulled from Kibana. Appended, not replaced.
    kibana_logs: Annotated[list[str], operator.add]
