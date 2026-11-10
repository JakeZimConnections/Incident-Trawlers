# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A LangGraph + Claude (`langchain-anthropic`) agent harness for investigating incidents. One shared agent loop runs many **workflows**, and each workflow picks its own state schema, tools and prompt. `architecture.md` has the full layout, the graph diagram and the "how to add a tool/state/workflow" steps. Read it before making structural changes, and keep it updated when they happen.

This folder is a git submodule of the parent `ML-Apprenticship` repo (`.git` points to `../.git/modules/Incident-Trawlers`).

## Commands

There is no build, lint or packaging config, and no `requirements.txt`. Dependencies are `langchain-anthropic` and `langgraph`, and `ANTHROPIC_API_KEY` must be set.

```bash
python3 main.py                              # run the "default" workflow
python3 main.py zim_incident                 # run a named workflow (choices come from WORKFLOWS)
python3 main.py zim_incident --prompt "..."  # override the workflow's prompt
```

Run from the repo root: imports like `from core import Workflow` and `from tools import TOOLS` rely on the root being on `sys.path`.

`sample_project/` is a test target, not part of the harness:

```bash
cd sample_project && pytest                                   # all tests
cd sample_project && pytest test_calculator.py::test_divide   # one test
```

**`calculator.divide` is deliberately broken** (`return a + b`), so the default workflow ("run the test suite, explain failures") has something to find. Don't fix it unless asked.

## Architecture: how the pieces connect

- `main.py` → `workflows.WORKFLOWS[name]` → `Workflow.run()` → `core.build_agent(state_schema, tools)` → compiled `StateGraph` looping `call_model ⇄ run_tools` until Claude makes no tool calls.
- **`core/` is the only place graph wiring lives.** `build_agent` creates the model *inside* the function (`make_model(tools)`), so each workflow's Claude only sees that workflow's tools. Don't reintroduce a module-level model.
- **Workflows are config, not code.** A `workflows/<name>.py` file defines `WORKFLOW = Workflow(...)` and must be registered in `workflows/__init__.py`, or `main.py` won't see it.
- **Every state schema must extend `state.AgentState`**, because `call_model` and `should_continue` read `state["messages"]`. Fields other than `messages` need starting values in the workflow's `initial_state`.
- **`ToolNode` only writes to `messages`.** Custom state fields (e.g. `ZimState.cognito_user`, `stripe_ref`, `kibana_logs`) are only filled if a workflow adds its own node to copy tool results into them. None exists yet.
- **Keep `core/` thin:** something goes there only once two workflows need it. Logic needed by one workflow stays in that workflow.
- Tools: one `@tool` function per file in `tools/`, exported from `tools/__init__.py`. Tools catch exceptions and return an `"Error: ..."` string rather than raising, so the agent can see and react to failures.

`sample_project/agent.py` (raw Anthropic SDK), `LCAgent.py` (LangChain `create_agent`) and `LGAgent.py` (LangGraph) are the original reference versions of the same agent. The harness was refactored out of `LGAgent.py`. Leave them as they are.

## Conventions

- Every file starts with a one-line `#` comment saying what the file is and why it's set up that way. Keep this for new files.
- Comments use a single `#`.
