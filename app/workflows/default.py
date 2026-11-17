# Default workflow: the original sample agent (inspect a project, run its tests), kept as a baseline.
from app.core.langgraph import Workflow
from app.core.langgraph.tools import TOOLS
from app.schemas.graph import AgentState

# The original sample agent: inspect a project and run its tests.
WORKFLOW = Workflow(
    name="default",
    state_schema=AgentState,
    tools=TOOLS,
    prompt=(
        "Inspect this project and run the test suite. "
        "Explain any failures you find."
    ),
)
