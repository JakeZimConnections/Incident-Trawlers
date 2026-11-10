# Tool: run a shell command and return its output; one tool per file so tools are easy to find, add and reuse.
import subprocess

from langchain_core.tools import tool


@tool
def run_shell(command: str) -> str:
    """Run a shell command and return its output."""
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
