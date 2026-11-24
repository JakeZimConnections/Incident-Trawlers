# Graph state schemas workflows choose from; every one extends AgentState so the shared loop always finds messages.
import operator
from typing import Annotated, Literal, TypedDict

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


# Where a document is in the doc intel pipeline; each later step moves it forward one stage.
DocStatus = Literal["discovered", "read", "classified", "routed", "failed"]


class DocumentRecord(TypedDict, total=False):
    """Everything known about one file. total=False: each stage fills in its own fields."""

    path: str  # relative to the inbox, e.g. "contracts/acme.pdf"; also the key in documents
    extension: str  # e.g. ".pdf"; used to pick a reader for binary files
    size_bytes: int
    status: DocStatus
    content_type: str  # what the content is, e.g. "incident report", "invoice", "log"
    summary: str  # one line
    suggested_workflow: str | None  # a name in WORKFLOWS, or None if nothing fits
    error: str | None  # why this file failed, when status is "failed"


class RAK_doc_intel_state(AgentState):
    """AgentState plus one record per document in the inbox, for the rakesh_doc_intel workflow."""

    # The folder being surveyed. Overwritten.
    inbox_path: str

    # One DocumentRecord per file, keyed by path. Merged (a | b), so a step can update
    # one file without resending the rest; a later update to the same path replaces it.
    documents: Annotated[dict[str, DocumentRecord], operator.or_]

    # Problems not tied to a single file (e.g. inbox missing). Appended, not replaced.
    errors: Annotated[list[str], operator.add]
