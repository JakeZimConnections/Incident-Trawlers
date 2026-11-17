# Request and response types for the runs and workflows routes, so FastAPI validates and documents them.
from pydantic import BaseModel


class RunRequest(BaseModel):
    """Body of POST /workflows/{name}/runs. Leave prompt out to use the workflow's default."""

    prompt: str | None = None


class RunResponse(BaseModel):
    """What a finished run returns."""

    workflow: str
    answer: str  # the last message Claude sent
    message_count: int  # how many messages the run produced, including tool calls
    trace_file: str  # tracelogs/<workflow>/workflow<datetime>.md
    langsmith_run_id: str | None = None  # search this in LangSmith; None when tracing is off


class WorkflowInfo(BaseModel):
    """One entry in GET /workflows."""

    name: str
    prompt: str
    tools: list[str]
