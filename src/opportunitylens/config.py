from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="OPPORTUNITYLENS_",
        extra="ignore",
    )

    environment: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"
    database_url: str = (
        "postgresql+asyncpg://opportunitylens:opportunitylens@localhost:5432/opportunitylens"
    )
    provider_timeout_seconds: float = Field(default=20.0, gt=0)
    provider_max_response_bytes: int = Field(default=5_000_000, gt=0)
    provider_concurrency: int = Field(default=4, gt=0)
    provider_retry_attempts: int = Field(default=2, ge=0)
    missing_runs_before_close: int = Field(default=2, gt=0)
    resume_max_bytes: int = Field(default=5 * 1024 * 1024, gt=0)
    rrf_k: int = Field(default=60, gt=0)
    retrieval_candidate_limit: int = Field(default=50, gt=0)
    rerank_limit: int = Field(default=20, gt=0)
    analysis_limit: int = Field(default=10, gt=0)


@lru_cache
def get_settings() -> Settings:
    return Settings()
