# FastAPI entry point: creates the app and mounts the v1 routes, so `uvicorn app.main:app` serves everything.
from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(title=settings.app_name)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health() -> dict:
    """Says the server is up."""
    return {"status": "ok"}
