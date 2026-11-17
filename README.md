# Incident-Trawlers

A FastAPI + LangGraph agent harness: one shared Claude agent loop that runs many workflows, each triggered over HTTP. See [architecture.md](architecture.md) for how it fits together.

## Quick start

```bash
brew install uv                                  # once
cp .env.example .env                             # add ANTHROPIC_API_KEY
uv sync
uv run uvicorn app.main:app --reload             # http://localhost:8000/docs
```

```bash
curl localhost:8000/api/v1/workflows
curl -X POST localhost:8000/api/v1/workflows/default/runs -H 'Content-Type: application/json' -d '{}'
```

Each run's trace is written to `tracelogs/<workflow>/`.
