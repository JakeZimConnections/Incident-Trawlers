# Tool: write content to a file; one tool per file so tools are easy to find, add and reuse.
from pathlib import Path

from langchain_core.tools import tool


@tool
def write_file(path: str, content: str) -> str:
    """Write content to a file, overwriting any existing content."""
    try:
        Path(path).write_text(content)
        return f"Wrote {len(content)} characters to {path}"

    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"
