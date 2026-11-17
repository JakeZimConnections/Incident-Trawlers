# LangSmith tracing: turns it on from settings at startup and gives each workflow its own LangSmith project.
import logging
import os

from app.core.config import settings

logger = logging.getLogger("trawlers")


def langsmith_enabled() -> bool:
    """True when LANGSMITH_TRACING is on and a key is set."""
    return settings.langsmith_tracing and bool(settings.langsmith_api_key)


def setup_langsmith() -> None:
    """Hand the LangSmith settings to the langsmith SDK.

    The SDK only reads environment variables, so this is the one place settings are copied into os.environ.
    Once set, LangGraph sends every run to LangSmith on its own.
    """
    if not langsmith_enabled():
        logger.info("LangSmith tracing off (set LANGSMITH_TRACING=true and LANGSMITH_API_KEY to turn it on)")
        return
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint
    logger.info(f"LangSmith tracing on → {settings.langsmith_endpoint}, projects {settings.langsmith_project}-<workflow>")


def langsmith_project(workflow_name: str) -> str:
    """One LangSmith project per workflow, so each gets its own run list and monitoring charts."""
    return f"{settings.langsmith_project}-{workflow_name}"
