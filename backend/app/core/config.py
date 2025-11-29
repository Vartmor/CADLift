from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    app_name: str = "CADLift Backend"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"
    debug: bool = True
    database_url: str = "sqlite+aiosqlite:///./cadlift.db"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7
    storage_path: str = "./storage"
    log_level: str = "INFO"
    redis_url: str = "redis://localhost:6379/0"
    enable_task_queue: bool = True
    llm_provider: str = "none"  # options: none, openai
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    llm_timeout_seconds: float = 30.0
    vision_api_url: str | None = None
    vision_api_key: str | None = None
    vision_timeout_seconds: float = 30.0
    max_upload_mb: int = 25


@lru_cache()
def get_settings() -> Settings:
    return Settings()
