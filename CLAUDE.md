# CLAUDE.md

FastAPI + LangGraph + Claude agent harness: one shared agent loop runs many **workflows**, each picking its own state schema, tools and prompt, triggered over HTTP. Layout follows the fastapi-langgraph-agent-production-ready-template minus its extras (auth, DB, memory, metrics).

**Read `architecture.md` before structural changes, and update it when they happen.**

**`setUpInstruction.md` is the setup guide (install, `.env`, LangSmith, run, troubleshooting). Update it whenever you add a tool, service, API key, setting or command someone needs to set up.**

This folder is a git submodule of `ML-Apprenticship` (`.git` → `../.git/modules/Incident-Trawlers`).

## Commands

uv is the package manager. Copy `.env.example` to `.env` and set `ANTHROPIC_API_KEY`. Run everything from the repo root (imports are absolute: `from app.core.langgraph import Workflow`).

```bash
uv sync
uv run uvicorn app.main:app --reload             # :8000, docs at /docs
curl -X POST localhost:8000/api/v1/workflows/default/runs -H 'Content-Type: application/json' -d '{"prompt": "..."}'
cd sample_project && uv run pytest               # test target for the default workflow
```

**`sample_project/calculator.divide` is deliberately broken** (`return a + b`) so the default workflow has something to find. Don't fix it unless asked. Leave `sample_project/agent.py`, `LCAgent.py` and `LGAgent.py` (the original reference agents) as they are.

## Rules

- **Routes hold no agent logic.** `app/api/` validates, looks up `WORKFLOWS[name]` and returns `app/schemas/run.py` types.
- **Graph wiring lives only in `app/core/langgraph/`.** `build_agent` creates the model inside the function, so each workflow's Claude only sees its own tools. Don't add a module-level model.
- **Keep `app/core/` thin:** add to it only once two workflows need something.
- **Workflows are config.** `app/workflows/<name>.py` defines `WORKFLOW = Workflow(...)` and must be added to `WORKFLOWS` in `app/workflows/__init__.py`.
- **State schemas extend `AgentState`** (`app/schemas/graph.py`); extra fields need starting values in `initial_state`. `ToolNode` only writes `messages`, so other fields need a node of their own.
- **Tools:** one `@tool` per file in `app/core/langgraph/tools/`. Catch exceptions and return `"Error: ..."`, never raise.
- **Settings:** `app/core/config.settings`, never `os.environ`. New setting → field on `Settings` + line in `.env.example`.
- **Logging:** use `log(message, level)` from `app/services/trace_logger.py`, never `print`. It goes to the terminal and the current run's trace file.
- `Workflow.run()` returns `(state, trace)` and writes every step to `tracelogs/<workflow>/workflow<datetime>.md`.
- **LangSmith:** set up only in `app/core/monitoring.py` (the one allowed `os.environ` write) and `Workflow.run()`. Each workflow traces to its own project, `<LANGSMITH_PROJECT>-<workflow>`. Off unless `LANGSMITH_TRACING=true`.

## Conventions

- Every file starts with a one-line `#` comment saying what it is and why it's set up that way.
- Comments use a single `#`.
