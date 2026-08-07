from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


_ENV_FILE = Path(__file__).resolve().parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    groq_api_key: str = Field(..., description="Groq API key from https://console.groq.com/keys")
    model_name: str = "llama-3.1-8b-instant"
    workspace_path: str = "workspace"
    max_fix_attempts: int = 3
    max_retries: int = 2
    log_level: str = "INFO"
    log_folder: str = "logs"
    run_timeout_seconds: int = 60
    checkpoint_db: str = "checkpoints/graph.db"


settings = Settings()
