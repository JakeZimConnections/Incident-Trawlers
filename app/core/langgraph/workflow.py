# Workflow dataclass bundling state, tools and prompt, so a new workflow is config, not new graph code.
from dataclasses import dataclass, field

from app.core.config import settings
from app.services.trace_logger import TraceLogger, current_trace

from .graph import build_agent


@dataclass
class Workflow:
    """One workflow: which state, which tools and which prompt to run the shared loop with."""

    name: str
    state_schema: type  # e.g. AgentState or ZimState, from app/schemas/graph.py
    tools: list  # the @tool functions this workflow may use, from app/core/langgraph/tools/
    prompt: str  # the default user message
    initial_state: dict = field(default_factory=dict)  # starting values for fields other than messages
    model_name: str | None = None  # None = settings.default_model
    recursion_limit: int | None = None  # None = settings.recursion_limit

    def build(self):
        """Compile this workflow's graph."""
        return build_agent(self.state_schema, self.tools, self.model_name)

    async def run(self, prompt: str | None = None) -> tuple[dict, TraceLogger]:
        """Run the workflow to END, logging every step, and return the final state and its trace."""
        agent = self.build()
        prompt = prompt or self.prompt
        state = {**self.initial_state, "messages": [("user", prompt)]}
        limit = self.recursion_limit or settings.recursion_limit
        trace = TraceLogger(self.name, prompt, self.model_name or settings.default_model, self.initial_state)

        final_state = state
        token = current_trace.set(trace)  # log() calls during this run go to this trace
        try:
            # "updates" = what each node returned (for the trace); "values" = the full state after it
            async for mode, chunk in agent.astream(
                state, config={"recursion_limit": limit}, stream_mode=["updates", "values"]
            ):
                if mode == "updates":
                    for node, update in chunk.items():
                        trace.log_update(node, update)
                else:
                    final_state = chunk
        except Exception as e:
            trace.fail(e)
            e.trace_file = str(trace.path)  # so the route can say where the trace is
            raise
        finally:
            current_trace.reset(token)

        trace.finish(final_state)
        return final_state, trace
