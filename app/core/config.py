from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Landing Backend"
    app_env: str = "development"
    app_debug: bool = False

    api_v1_prefix: str = "/api"

    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    owner_email: str = "owner@example.com"

    # AI provider settings (OpenRouter-compatible OpenAI SDK client).
    openai_api_key: str | None = None
    openai_base_url: str = "https://openrouter.ai/api/v1"
    openai_model: str = "openai/gpt-4o-mini"
    openai_timeout_seconds: int = 8

    rate_limit_max_requests: int = 5
    rate_limit_window_seconds: int = 60

    storage_dir: Path = Path("app/storage")
    database_url: str = "sqlite:///./app/storage/landing.db"
    log_dir: Path = Path("logs")
    request_log_file: Path = Path("logs/requests.log")
    app_log_file: Path = Path("logs/app.log")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def parsed_cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()

    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    settings.log_dir.mkdir(parents=True, exist_ok=True)

    return settings
