# Typed settings read from .env, so config lives in one place instead of os.environ calls everywhere.
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings. Each field can be set in .env or as an environment variable of the same name."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Incident-Trawlers"
    api_v1_prefix: str = "/api/v1"
    anthropic_api_key: str = ""
    default_model: str = "claude-sonnet-5-5"
    recursion_limit: int = (
        20  # graph-level safety limit: each node visit counts as a step
    )
    tracelog_dir: str = (
        "tracelogs"  # one Markdown trace per run: <dir>/<workflow>/workflow<datetime>.md
    )
    log_level: str = "info"  # terminal logging: debug | info | warning | error
    langsmith_tracing: bool = False  # send every run to LangSmith
    langsmith_api_key: str = ""
    langsmith_endpoint: str = "https://eu.api.smith.langchain.com"  # EU region
    langsmith_project: str = (
        "incident-trawlers"  # prefix: each workflow traces to <prefix>-<workflow>
    )


settings = Settings()
