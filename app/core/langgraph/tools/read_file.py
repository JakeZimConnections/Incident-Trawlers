# Tool: read a file or list a directory; one tool per file so tools are easy to find, add and reuse.
from pathlib import Path

from langchain_core.tools import tool


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
