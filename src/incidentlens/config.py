from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="INCIDENTLENS_",
        extra="ignore",
    )

    environment: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"
    scenario_root: Path = Path("scenarios")
    qdrant_url: str | None = None
    qdrant_path: Path = Path("var/qdrant")
    qdrant_collection: str = "incident_evidence"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:4b"
    ollama_timeout_seconds: float = Field(default=120.0, gt=0)


@lru_cache
def get_settings() -> Settings:
    return Settings()
