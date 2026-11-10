# Architecture

> **One shared agent loop (`core/`), many workflows.** A workflow is just config: which state, which tools, which prompt.

## Layout

```
Incident-Trawlers/
  main.py              # CLI: pick a workflow by name and run it
  core/                # the engine, shared by every workflow
    model.py           #   make_model(tools): Claude bound to a tool list
    graph.py           #   build_agent(state_schema, tools): the LangGraph loop + should_continue
    workflow.py        #   Workflow dataclass: name, state, tools, prompt, initial_state, limits
  workflows/           # one file per workflow (config only)
    __init__.py        #   WORKFLOWS registry: {name: Workflow}
    default.py         #   original sample agent: inspect a project, run its tests
    zim_incident.py    #   ZIM incident: gather Cognito, Stripe and Kibana evidence
  state/               # state schemas workflows choose from
    agent_state.py     #   AgentState: messages only (the base)
    zim_state.py       #   ZimState: AgentState + cognito_user, stripe_ref, kibana_logs
  tools/               # one @tool per file
    read_file.py, write_file.py, run_shell.py
    __init__.py        #   exports each tool + TOOLS (all of them)
  sample_project/      # the original example (LGAgent.py etc.) and a tiny test target
```

## The graph (same for every workflow)

```
START → call_model ──tool calls?──yes──▶ run_tools ─┐
            ▲            │                          │
            │            no → END                   │
            └───────────────────────────────────────┘
```

- `call_model`: sends `state["messages"]` to Claude and appends the reply.
- `should_continue`: if the last reply has tool calls, go to `run_tools`, otherwise `END`.
- `run_tools`: LangGraph's `ToolNode`, which runs the requested tools and appends the results as messages.
- `recursion_limit` (default 20) caps the number of node visits.

## How a run flows

1. `python3 main.py zim_incident` → `main.py` looks up `WORKFLOWS["zim_incident"]`.
2. `Workflow.run()` → `build_agent(ZimState, tools)` compiles the graph.
3. Starting state = `initial_state` + the user prompt as `messages`.
4. The graph loops until Claude stops calling tools, then prints the last message.

## Why it's split like this

| Folder | Why |
|---|---|
| `core/` | **Write the loop once.** Every workflow gets the same, tested engine |
| `workflows/` | **New workflow = new config file**, not new graph code |
| `state/` | **Several state schemas**, each extending `AgentState` so the core loop (which needs `messages`) always works |
| `tools/` | **Pick-and-mix.** Each workflow takes only the tools it needs, and Claude only sees those |

**Rule for `core/`:** keep it to what every workflow shares. If only one workflow needs something (an extra node, a different graph shape), it lives in that workflow. Move it into `core/` only once a second workflow needs it.

## State

- A node returns only the fields it changes.
- **Field without a reducer → overwritten.** E.g. `cognito_user`, `stripe_ref`.
- **Field with a reducer → merged.** `messages` uses `add_messages` and `kibana_logs` uses `operator.add`, so both append.
- `ToolNode` only updates `messages`. To fill other fields (e.g. `ZimState`'s), add a node after `run_tools` that copies tool results into them.

## Adding things

| To add | Do this |
|---|---|
| A tool | `tools/<name>.py` with a `@tool` function, then export it from `tools/__init__.py` |
| A state | `state/<name>.py` extending `AgentState`, then export it from `state/__init__.py` |
| A workflow | `workflows/<name>.py` with `WORKFLOW = Workflow(...)`, then add it to `WORKFLOWS` in `workflows/__init__.py` |

## Running

From `Incident-Trawlers/`, with `langchain-anthropic` and `langgraph` installed and `ANTHROPIC_API_KEY` set:

```bash
python3 main.py                                  # default workflow
python3 main.py zim_incident                     # ZIM incident workflow
python3 main.py zim_incident --prompt "..."      # override the prompt
```

## Not built yet

- Cognito, Stripe and Kibana tools (`zim_incident` only has `read_file` and `run_shell` for now).
- A node that writes tool results into `ZimState`'s `cognito_user`, `stripe_ref` and `kibana_logs`.
