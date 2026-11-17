# Architecture

> **A FastAPI server around one shared agent loop that runs many workflows.** A workflow is just config: which state, which tools, which prompt.

Folder layout follows [fastapi-langgraph-agent-production-ready-template](https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template), without auth, database, memory or metrics.

## Layout

```
Incident-Trawlers/
  pyproject.toml · .python-version · .env.example   # uv project, Python version, settings template
  app/
    main.py                 # FastAPI app: mounts /api/v1 + GET /health, sets up logging
    api/v1/
      api.py                #   joins the routers below
      workflows.py          #   GET  /api/v1/workflows
      runs.py               #   POST /api/v1/workflows/{name}/runs
    core/
      config.py             #   Settings from .env
      logging.py            #   terminal logger ("trawlers")
      langgraph/            #   the engine, shared by every workflow
        graph.py            #     build_agent(state_schema, tools)
        workflow.py         #     Workflow dataclass + run()
        tools/              #     one @tool per file
    schemas/
      run.py                #   API types: RunRequest, RunResponse, WorkflowInfo
      graph.py              #   state: AgentState (base), ZimState
    services/
      llm.py                #   make_model(tools)
      trace_logger.py       #   TraceLogger + log()
    workflows/              #   one config file per workflow + WORKFLOWS registry
  tracelogs/                # gitignored, one Markdown file per run
  sample_project/           # test target + original reference agents
```

## How a request flows

```
POST /api/v1/workflows/{name}/runs  {"prompt": "..."}
  │
  ▼
api/v1/runs.py ──WORKFLOWS[name] (404 if missing)──▶ workflows/<name>.py
                                                        │ await workflow.run(prompt)
                                                        ▼
                                    core/langgraph/workflow.py ──build_agent──▶ graph.py ──make_model──▶ services/llm.py ──▶ Claude
                                                        │
                                                        ▼
              START → call_model ──tool calls?──yes──▶ run_tools ─┐
                          ▲            │ no                       │
                          │            ▼                          │
                          │           END                         │
                          └───────────────────────────────────────┘
                                                        │ every step ──▶ trace_logger ──▶ tracelogs/ + terminal
                                                        ▼
                         RunResponse {workflow, answer, message_count, trace_file}
```

- `call_model` sends `state["messages"]` to Claude and appends the reply.
- `should_continue` goes to `run_tools` if the reply has tool calls, otherwise `END`.
- `run_tools` is LangGraph's `ToolNode`: runs the tools, appends the results.
- `recursion_limit` (default 20) caps node visits.
- `GET /api/v1/workflows` lists the same `WORKFLOWS` registry.

## Why it's split like this

| Folder | Why |
|---|---|
| `api/` | **Routes only.** Check the request, hand off |
| `schemas/` | **Types in one place:** API bodies and graph state |
| `core/langgraph/` | **Write the loop once.** Keep it to what every workflow shares |
| `services/` | **Shared helpers** the engine calls (model, tracing) |
| `workflows/` | **New workflow = new config file**, instantly on the API |
| `tools/` | **Pick-and-mix.** Claude only sees the tools its workflow chose |

## State

- A node returns only the fields it changes.
- **No reducer → overwritten** (e.g. `cognito_user`). **Reducer → merged** (`messages` via `add_messages`, `kibana_logs` via `operator.add`).
- `ToolNode` only updates `messages`. To fill other fields, add a node after `run_tools`.

## Trace logs and `log()`

**Every run writes `tracelogs/<workflow>/workflow<YYYY-MM-DD_HH-MM-SS>.md`**, one step at a time, so a crashed run still leaves its trace. The path comes back as `trace_file` (also in the 502 error body).

- File: header (model, start time), prompt, `## Step N` per node (Claude's text, tool calls, tool results, tokens), then `## Result` (status, duration, steps, tokens).
- Terminal: a one-line summary per step. `LOG_LEVEL` sets how much.

```python
from app.services.trace_logger import log
log("Found 3 matching users")                  # debug | info | warning | error
```

- Prints `HH:MM:SS LEVEL [workflow] message` to the terminal.
- During a run, also adds it to that run's trace. A `ContextVar` (`current_trace`) keeps concurrent runs in their own files.

## Adding things

| To add | Do this |
|---|---|
| A tool | `app/core/langgraph/tools/<name>.py` with `@tool`, export from its `__init__.py` |
| A state | Class extending `AgentState` in `app/schemas/graph.py` |
| A workflow | `app/workflows/<name>.py` with `WORKFLOW = Workflow(...)`, add to `WORKFLOWS` |
| A route | Router in `app/api/v1/<name>.py`, include it in `app/api/v1/api.py` |
| A setting | Field on `Settings` in `app/core/config.py` + line in `.env.example` |

## Not built yet

- Runs block: the request waits until the workflow finishes.
- `zim_incident` has only `read_file` and `run_shell`, and nothing fills `ZimState`'s extra fields yet.
