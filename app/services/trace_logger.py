# Writes one Markdown trace per run to tracelogs/<workflow>/workflow<datetime>.md, step by step, and echoes it to the terminal.
import json
import logging
import time
from contextvars import ContextVar
from datetime import datetime
from pathlib import Path

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage

from app.core.config import settings

logger = logging.getLogger("trawlers")  # terminal output, set up in app/core/logging.py

# The trace of the run happening right now. Set by Workflow.run(), read by log().
# A ContextVar keeps two runs at the same time from writing into each other's file.
current_trace: ContextVar["TraceLogger | None"] = ContextVar("current_trace", default=None)


def log(message: str, level: str = "info") -> None:
    """Log a line to the terminal and, during a run, to that run's trace file.

    Call it from anywhere: a workflow, a tool, a node. level = debug | info | warning | error.
    """
    trace = current_trace.get()
    prefix = f"[{trace.workflow}] " if trace else ""
    getattr(logger, level, logger.info)(prefix + message)
    if trace:
        trace.note(message, level)


def _short(text: str, limit: int = 120) -> str:
    """First line of text, cut to limit, for one-line terminal summaries."""
    first = text.strip().splitlines()[0] if text.strip() else ""
    return first if len(first) <= limit else first[: limit - 1] + "…"


class TraceLogger:
    """Appends each graph step to a Markdown file as the run happens."""

    def __init__(self, workflow_name: str, prompt: str, model: str, initial_state: dict):
        self.workflow = workflow_name
        folder = Path(settings.tracelog_dir) / workflow_name
        folder.mkdir(parents=True, exist_ok=True)

        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.path = folder / f"workflow{stamp}.md"
        n = 2
        while self.path.exists():  # two runs in the same second get _2, _3...
            self.path = folder / f"workflow{stamp}_{n}.md"
            n += 1

        self.started = time.monotonic()
        self.step = 0
        self.input_tokens = 0
        self.output_tokens = 0

        extra = {k: v for k, v in initial_state.items() if k != "messages"}
        self._write(
            f"# Run: {workflow_name}\n\n"
            f"| | |\n|---|---|\n"
            f"| Started | {datetime.now():%Y-%m-%d %H:%M:%S} |\n"
            f"| Model | `{model}` |\n"
            + (f"| Initial state | `{json.dumps(extra, default=str)}` |\n" if extra else "")
            + f"\n## Prompt\n\n{prompt}\n"
        )
        logger.info(f"[{self.workflow}] ▶ started · trace: {self.path}")
        logger.info(f"[{self.workflow}]   prompt: {_short(prompt)}")

    def log_update(self, node: str, update: dict | None) -> None:
        """Log what one node returned (one graph step)."""
        self.step += 1
        lines = [f"\n## Step {self.step}: `{node}` (+{self._elapsed()})\n"]

        for msg in (update or {}).get("messages", []):
            lines.append(self._message(msg))

        for key, value in (update or {}).items():  # custom state fields, e.g. ZimState's
            if key != "messages":
                lines.append(f"**State `{key}`** ←\n\n```json\n{json.dumps(value, indent=2, default=str)}\n```\n")
                logger.info(f"[{self.workflow}]   state {key} updated")

        self._write("\n".join(lines))

    def note(self, message: str, level: str = "info") -> None:
        """Add a log() line to the trace, in between steps."""
        self._write(f"\n> **{level.upper()}** (+{self._elapsed()}) {message}\n")

    def finish(self, final_state: dict) -> None:
        """Log the final answer and totals."""
        answer = final_state["messages"][-1].text if final_state.get("messages") else ""
        self._write(
            f"\n## Result\n\n{answer}\n\n"
            f"| | |\n|---|---|\n"
            f"| Status | ✅ finished |\n"
            f"| Duration | {self._elapsed()} |\n"
            f"| Steps | {self.step} |\n"
            f"| Tokens | {self.input_tokens:,} in / {self.output_tokens:,} out |\n"
        )
        logger.info(
            f"[{self.workflow}] ✅ finished in {self._elapsed()} · {self.step} steps · "
            f"{self.input_tokens:,} in / {self.output_tokens:,} out tokens"
        )

    def fail(self, error: Exception) -> None:
        """Log why the run stopped."""
        self._write(
            f"\n## Result\n\n"
            f"| | |\n|---|---|\n"
            f"| Status | ❌ failed |\n"
            f"| Error | `{type(error).__name__}: {error}` |\n"
            f"| Duration | {self._elapsed()} |\n"
            f"| Steps | {self.step} |\n"
            f"| Tokens | {self.input_tokens:,} in / {self.output_tokens:,} out |\n"
        )
        logger.error(f"[{self.workflow}] ❌ failed after {self._elapsed()}: {type(error).__name__}: {error}")

    def _message(self, msg: BaseMessage) -> str:
        """Markdown for one message, plus a one-line terminal summary."""
        tag = f"[{self.workflow}]   step {self.step}"

        if isinstance(msg, AIMessage):
            usage = msg.usage_metadata or {}
            self.input_tokens += usage.get("input_tokens", 0)
            self.output_tokens += usage.get("output_tokens", 0)

            parts = []
            if msg.text:
                parts.append(f"**Claude:**\n\n{msg.text}\n")
                logger.info(f"{tag} claude: {_short(msg.text)}")
            for call in msg.tool_calls:
                args = json.dumps(call["args"], indent=2, default=str)
                parts.append(f"**Tool call → `{call['name']}`**\n\n```json\n{args}\n```\n")
                logger.info(f"{tag} → {call['name']} {_short(json.dumps(call['args'], default=str), 100)}")
            if usage:
                parts.append(f"_Tokens: {usage.get('input_tokens', 0):,} in / {usage.get('output_tokens', 0):,} out_\n")
            return "\n".join(parts)

        if isinstance(msg, ToolMessage):
            failed = msg.status == "error" or msg.text.startswith("Error:")
            status = " (error)" if failed else ""
            (logger.warning if failed else logger.info)(
                f"{tag} ← {msg.name}{status}: {_short(msg.text, 100)} ({len(msg.text):,} chars)"
            )
            return f"**Tool result ← `{msg.name}`{status}**\n\n```text\n{msg.text}\n```\n"

        logger.info(f"{tag} {msg.type}: {_short(msg.text)}")
        return f"**{msg.type}:**\n\n{msg.text}\n"

    def _elapsed(self) -> str:
        return f"{time.monotonic() - self.started:.1f}s"

    def _write(self, text: str) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(text)
