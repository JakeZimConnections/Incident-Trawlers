# Incident-Trawlers

A FastAPI + LangGraph agent harness: one shared Claude agent loop that runs many workflows, each triggered over HTTP. See [architecture.md](architecture.md) for how it fits together, or the [interactive diagram on GitDiagram](https://gitdiagram.com/jakezimconnections/incident-trawlers).

## Quick start

Full setup (keys, LangSmith, troubleshooting): [setUpInstruction.md](setUpInstruction.md).

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

Postman collection: `postman/Incident-Trawlers.postman_collection.json`.

## Run with Docker

Docker Desktop open, from this folder:

```bash
cp .env.example .env          # once; then put your ANTHROPIC_API_KEY in .env
docker compose up --build     # builds the image and starts the API on http://localhost:8000/docs
curl localhost:8000/health    # {"status":"ok"}
```

| Do | Command |
|---|---|
| Run in the background | `docker compose up --build -d` |
| See logs (background mode) | `docker compose logs -f` |
| Stop | `Ctrl+C`, or `docker compose down` if it's in the background |
| Restart after editing `.env` | `docker compose up -d --force-recreate` |
| Rebuild after code changes | `docker compose up --build` |

"env file .env not found" means you skipped the `cp` step.

## Traces

Each run's trace is written to `tracelogs/<workflow>/`. For LangSmith too, set `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` in `.env`; each workflow gets its own project.
