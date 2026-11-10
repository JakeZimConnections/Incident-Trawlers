import subprocess
from pathlib import Path

from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langchain.agents import create_agent

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

model = ChatAnthropic(
    model="claude-sonnet-4-6",
    max_tokens=16384,
)

agent = create_agent(
    model=model,
    tools=[read_file, write_file, run_shell],
    system_prompt=(
        "You are a coding assistant. Inspect files before changing them, "
        "and run relevant tests after making changes."
    ),
)

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Inspect this project and tell me what tests it has.",
            }
        ]
    }
)

print(result["messages"][-1].content)
