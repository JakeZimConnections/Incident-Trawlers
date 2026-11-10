# Builds the model -> tools -> model LangGraph loop for any state and tools, so workflows don't rewrite it.
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from .model import DEFAULT_MODEL, make_model


def should_continue(state: dict) -> str:  # reads the state to pick the next node
    """Run tools if Claude asked for any, otherwise finish."""
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "run_tools"

    return END


def build_agent(state_schema: type, tools: list, model_name: str = DEFAULT_MODEL):
    """Build the model -> tools -> model loop for any state schema and tool list."""
    model = make_model(tools, model_name)  # bound to this workflow's tools only

    def call_model(state: dict) -> dict:  # reads the current state, returns a state update
        """Ask Claude for the next response."""
        return {"messages": [model.invoke(state["messages"])]}

    builder = StateGraph(state_schema)  # every node shares this state shape

    builder.add_node("call_model", call_model)
    builder.add_node("run_tools", ToolNode(tools))  # runs whichever tool Claude asked for

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

    return builder.compile()
