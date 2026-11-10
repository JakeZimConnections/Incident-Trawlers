import anthropic
import subprocess
from pathlib import Path

client = anthropic.Anthropic()

TOOLS = [
    {
        "name": "read_file",
        "description": "Read a file, or list the names in a directory.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a file, overwriting any existing content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "run_shell",
        "description": "Run a shell command and return its output. Use this to run tests, check git status, list files, etc.",
        "input_schema": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    },
]

def read_file(path: str) -> str:
    target = Path(path)
    if target.is_dir():
        return "\n".join(p.name for p in target.iterdir())
    return target.read_text()

def write_file(path: str, content: str) -> str:
    Path(path).write_text(content)
    return f"Wrote {len(content)} characters to {path}"

def run_shell(command: str) -> str:
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    output = result.stdout + result.stderr
    return f"Exit code: {result.returncode}\n{output}"

def run_tool(name: str, arguments: dict) -> str:
    try:
        if name == "read_file":
            return read_file(arguments["path"])
        if name == "write_file":
            return write_file(arguments["path"], arguments["content"])
        if name == "run_shell":
            return run_shell(arguments["command"])
        return f"Error: unknown tool '{name}'"
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"

def agent(prompt: str, max_turns: int = 10) -> str:
    messages = [{"role": "user", "content": prompt}]

    for turn in range(1, max_turns + 1):
        print(f"\n--- Turn {turn} ---")

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=16384,
            tools=TOOLS,
            messages=messages,
        )

        assistant_message = {"role": "assistant", "content": response.content}
        messages.append(assistant_message)

        tool_results = []
        for block in response.content:
            if block.type == "text":
                print(f"[assistant] {block.text}")
            elif block.type == "tool_use":
                print(f"[tool call] {block.name}({block.input})")
                result = run_tool(block.name, block.input)
                is_error = result.startswith("Error:")
                print(f"[tool result] {result[:200]}{'...' if len(result) > 200 else ''}")
                tool_result = {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                    "is_error": is_error,
                }
                tool_results.append(tool_result)

        if response.stop_reason == "end_turn":
            return next((b.text for b in response.content if b.type == "text"), "")
        if not tool_results:
            raise RuntimeError(f"Model stopped without tool calls: {response.stop_reason}")

        tool_results_message = {"role": "user", "content": tool_results}
        messages.append(tool_results_message)

    raise RuntimeError(f"Agent did not terminate within {max_turns} turns")