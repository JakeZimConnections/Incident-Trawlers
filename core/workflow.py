# Workflow dataclass bundling state, tools and prompt, so a new workflow is config, not new graph code.
from dataclasses import dataclass, field

from .graph import build_agent
from .model import DEFAULT_MODEL


@dataclass
class Workflow:
    """One workflow: which state, which tools and which prompt to run the core loop with."""

    name: str
    state_schema: type  # e.g. AgentState or ZimState, from state/
    tools: list  # the @tool functions this workflow may use, from tools/
    prompt: str  # the default user message
    initial_state: dict = field(default_factory=dict)  # starting values for fields other than messages
    model_name: str = DEFAULT_MODEL
    recursion_limit: int = 20  # graph-level safety limit: each node visit counts as a step

    def build(self):
        """Compile this workflow's graph."""
        return build_agent(self.state_schema, self.tools, self.model_name)

    def run(self, prompt: str | None = None) -> dict:
        """Run the workflow and return the final state."""
        agent = self.build()
        state = {**self.initial_state, "messages": [("user", prompt or self.prompt)]}
        return agent.invoke(state, config={"recursion_limit": self.recursion_limit})
