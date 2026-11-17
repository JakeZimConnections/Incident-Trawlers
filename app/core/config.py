# Typed settings read from .env, so config lives in one place instead of os.environ calls everywhere.
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings. Each field can be set in .env or as an environment variable of the same name."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Incident-Trawlers"
    api_v1_prefix: str = "/api/v1"
    anthropic_api_key: str = ""
    default_model: str = "claude-sonnet-4-6"
    recursion_limit: int = 20  # graph-level safety limit: each node visit counts as a step
    tracelog_dir: str = "tracelogs"  # one Markdown trace per run: <dir>/<workflow>/workflow<datetime>.md
    log_level: str = "info"  # terminal logging: debug | info | warning | error


settings = Settings()
