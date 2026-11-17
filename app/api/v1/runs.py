# POST /workflows/{name}/runs: runs one workflow to the end and returns its answer.
from fastapi import APIRouter, HTTPException

from app.schemas.run import RunRequest, RunResponse
from app.workflows import WORKFLOWS

router = APIRouter()


@router.post("/{name}/runs", response_model=RunResponse)
async def run_workflow(name: str, request: RunRequest) -> RunResponse:
    """Look the workflow up by name, run it, and return the last message."""
    workflow = WORKFLOWS.get(name)
    if workflow is None:
        raise HTTPException(status_code=404, detail=f"No workflow called '{name}'. See GET /workflows.")

    try:
        state, trace = await workflow.run(request.prompt)
    except Exception as e:  # e.g. a model error or hitting the recursion limit
        trace_file = getattr(e, "trace_file", None)
        raise HTTPException(status_code=502, detail={"error": f"{type(e).__name__}: {e}", "trace_file": trace_file})

    messages = state["messages"]
    return RunResponse(
        workflow=name,
        answer=messages[-1].text,
        message_count=len(messages),
        trace_file=str(trace.path),
    )
