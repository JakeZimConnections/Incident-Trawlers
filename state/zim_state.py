# ZIM incident state: AgentState plus Cognito, Stripe and Kibana fields, so evidence is stored, not just chatted.
import operator
from typing import Annotated

from .agent_state import AgentState


class ZimState(AgentState):
    """AgentState plus the evidence gathered while investigating a ZIM incident."""

    # Gather Cognito: the user's Cognito details (e.g. sub, email, status). Overwritten.
    cognito_user: dict | None

    # Gather Stripe ref: the Stripe payment reference (e.g. a payment intent ID). Overwritten.
    stripe_ref: str | None

    # Access Kibana logs: log lines pulled from Kibana. Appended, not replaced.
    kibana_logs: Annotated[list[str], operator.add]
