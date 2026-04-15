import json
from pathlib import Path
from typing import Any, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Fashion Inspiration API"
    app_env: str = "development"
    cors_origins: list[str] = ["http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value]
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                parsed: Any = json.loads(stripped)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
            return [stripped]
        return ["http://localhost:3000"]

    # Database: set database_url for Postgres, e.g. postgresql+psycopg://user:pass@localhost:5432/fashion
    database_url: str | None = None
    database_path: str = "backend/data/library.db"
    seed_demo_data: bool = True

    # Public URL prefix for stored assets (no trailing slash)
    public_assets_base_url: str = "http://localhost:8000"

    storage_backend: Literal["local", "s3"] = "local"
    storage_root: str = "backend/data"

    s3_bucket: str | None = None
    s3_region: str | None = None
    s3_endpoint_url: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    s3_key_prefix: str = "uploads"

    # heuristic | openai (requires OPENAI_API_KEY)
    classifier_backend: Literal["heuristic", "openai"] = "heuristic"
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    # sync: classify before response; background: FastAPI BackgroundTasks; arq: Redis worker
    classification_execution: Literal["sync", "background", "arq"] = "sync"
    redis_url: str | None = None

    log_level: str = "INFO"
    classification_max_retries: int = 3

    @property
    def database_file(self) -> Path:
        return Path(self.database_path)

    @property
    def uploads_dir(self) -> Path:
        return Path(self.storage_root) / "uploads"

    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        path = self.database_file.resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{path.as_posix()}"


settings = Settings()
