# Setup

Everything needed to get Incident-Trawlers running, from a fresh machine to a traced run. **Add a section here whenever a new tool, service or key is needed.**

## 1. Install

| Tool | Why | Install |
|---|---|---|
| uv | Python package manager; installs Python 3.13 for you | `brew install uv` |
| git | Repo is a submodule of `ML-Apprenticship` | `git submodule update --init` from the parent repo |

```bash
uv sync                      # creates .venv and installs everything in pyproject.toml
```

## 2. Configure `.env`

```bash
cp .env.example .env
```

| Setting | Required | Where to get it |
|---|---|---|
| `ANTHROPIC_API_KEY` | **Yes** | console.anthropic.com → API Keys |
| `DEFAULT_MODEL` | No | Default `claude-sonnet-4-6` |
| `RECURSION_LIMIT` | No | Default `20` node visits per run |
| `TRACELOG_DIR` | No | Default `tracelogs` |
| `LOG_LEVEL` | No | `debug` \| `info` \| `warning` \| `error` |
| `LANGSMITH_*` | No | See step 3 |

**Never commit `.env`.** It's gitignored; only `.env.example` is tracked.

## 3. LangSmith (optional: monitoring and debugging)

1. Sign in at https://eu.smith.langchain.com (**EU region**).
2. Settings → API Keys → create a key.
3. In `.env`:
   ```
   LANGSMITH_TRACING=true
   LANGSMITH_API_KEY=lsv2_...
   LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
   LANGSMITH_PROJECT=incident-trawlers
   ```
4. Restart the server. The terminal says `LangSmith tracing on`.

- **Projects are created automatically**, one per workflow: `incident-trawlers-<workflow>`.
- Find a run by the `langsmith_run_id` in the API response or the trace file header.

## 4. Run

```bash
uv run uvicorn app.main:app --reload             # http://localhost:8000/docs
```

```bash
curl localhost:8000/health                                   # {"status":"ok"}
curl localhost:8000/api/v1/workflows                         # list workflows
curl -X POST localhost:8000/api/v1/workflows/default/runs \
  -H 'Content-Type: application/json' -d '{}'                # run with its default prompt
```

**Check:** a new file appears in `tracelogs/default/`, and (if on) a run in LangSmith project `incident-trawlers-default`.

## 5. Test target

```bash
cd sample_project && uv run pytest               # fails on purpose: calculator.divide is broken
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `uv: command not found` | `brew install uv`, then open a new terminal |
| `ModuleNotFoundError: app` | Run from the repo root, not inside `app/` |
| 502 with `AuthenticationError` | `ANTHROPIC_API_KEY` missing or wrong in `.env` |
| 502 with `GraphRecursionError` | Raise `RECURSION_LIMIT` or tighten the prompt |
| Nothing in LangSmith | `LANGSMITH_TRACING=true`, key set, EU endpoint, server restarted |
