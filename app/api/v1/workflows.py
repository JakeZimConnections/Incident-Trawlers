# GET /workflows: lists the registry, so callers can see which workflows they can run.
from fastapi import APIRouter

from app.schemas.run import WorkflowInfo
from app.workflows import WORKFLOWS

router = APIRouter()


@router.get("", response_model=list[WorkflowInfo])
async def list_workflows() -> list[WorkflowInfo]:
    """Every workflow by name, with its default prompt and tool names."""
    return [
        WorkflowInfo(name=w.name, prompt=w.prompt, tools=[t.name for t in w.tools])
        for w in WORKFLOWS.values()
    ]
