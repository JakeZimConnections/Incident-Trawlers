# Collects every v1 router into one, so app/main.py mounts a single router.
from fastapi import APIRouter

from app.api.v1 import runs, workflows

api_router = APIRouter()
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(runs.router, prefix="/workflows", tags=["runs"])
