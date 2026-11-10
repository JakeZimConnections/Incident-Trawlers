import subprocess
from pathlib import Path
from typing import Annotated, TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

@tool
def read_file(path: str) -> str:
    """Read a file, or list the names in a directory."""
    try:
        target = Path(path)

        if target.is_dir():
            return "\n".join(p.name for p in target.iterdir())

        return target.read_text()

    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"

@tool
def write_file(path: str, content: str) -> str:
    """Write content to a file, overwriting any existing content."""
    try:
        Path(path).write_text(content)
        return f"Wrote {len(content)} characters to {path}"

    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"

@tool
def run_shell(command: str) -> str:
    """Run a Windows shell command and return its output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout + result.stderr
        return f"Exit code: {result.returncode}\n{output}"

    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"

tools = [read_file, write_file, run_shell]

model = ChatAnthropic(
    model="claude-sonnet-4-6",
    max_tokens=16384,
).bind_tools(tools)

class AgentState(TypedDict):
    # This reducer appends new messages instead of replacing old ones.
    messages: Annotated[list[BaseMessage], add_messages]

def call_model(state: AgentState) -> dict:
    """Ask Claude for the next response."""
    response = model.invoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: AgentState) -> str:
    """Choose the next graph edge after Claude responds."""
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "run_tools"

    return END

builder = StateGraph(AgentState)

builder.add_node("call_model", call_model)
builder.add_node("run_tools", ToolNode(tools))

builder.add_edge(START, "call_model")

builder.add_conditional_edges(
    "call_model",
    should_continue,
    {
        "run_tools": "run_tools",
        END: END,
    },
)

builder.add_edge("run_tools", "call_model")

agent = builder.compile()

result = agent.invoke(
    {
        "messages": [
            (
                "user",
                "Inspect this project and run the test suite. "
                "Explain any failures you find.",
            )
        ]
    },
    # A graph-level safety limit. Each node visit counts as a step.
    config={"recursion_limit": 20},
)

print(result["messages"][-1].content)