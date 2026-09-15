import pytest
from pydantic import ValidationError

from opportunitylens.config import Settings, get_settings


def test_provider_timeout_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        Settings(provider_timeout_seconds=0)


def test_default_upload_limit_is_five_mebibytes() -> None:
    assert Settings().resume_max_bytes == 5 * 1024 * 1024


def test_settings_have_opportunitylens_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.database_url == (
        "postgresql+asyncpg://opportunitylens:opportunitylens@localhost:5432/opportunitylens"
    )
    assert settings.provider_timeout_seconds == 20.0
    assert settings.provider_max_response_bytes == 5_000_000
    assert settings.provider_concurrency == 4
    assert settings.provider_retry_attempts == 2
    assert settings.missing_runs_before_close == 2
    assert settings.rrf_k == 60
    assert settings.retrieval_candidate_limit == 50
    assert settings.rerank_limit == 20
    assert settings.analysis_limit == 10


def test_settings_read_opportunitylens_environment_variables(monkeypatch) -> None:
    monkeypatch.setenv("OPPORTUNITYLENS_PROVIDER_TIMEOUT_SECONDS", "15")
    monkeypatch.setenv("OPPORTUNITYLENS_ANALYSIS_LIMIT", "7")

    settings = Settings(_env_file=None)

    assert settings.provider_timeout_seconds == 15.0
    assert settings.analysis_limit == 7


def test_get_settings_reuses_first_loaded_configuration(monkeypatch) -> None:
    monkeypatch.setenv("OPPORTUNITYLENS_ANALYSIS_LIMIT", "7")
    get_settings.cache_clear()

    try:
        first_settings = get_settings()

        monkeypatch.setenv("OPPORTUNITYLENS_ANALYSIS_LIMIT", "3")
        second_settings = get_settings()

        assert second_settings is first_settings
        assert second_settings.analysis_limit == 7
    finally:
        get_settings.cache_clear()
