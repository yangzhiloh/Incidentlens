from pathlib import Path

import pytest
from pydantic import ValidationError

from incidentlens import config
from incidentlens.config import Settings


def test_settings_have_free_local_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.scenario_root == Path("scenarios")
    assert settings.qdrant_url is None
    assert settings.qdrant_path == Path("var/qdrant")
    assert settings.qdrant_collection == "incident_evidence"
    assert settings.embedding_model == "BAAI/bge-small-en-v1.5"
    assert settings.ollama_base_url == "http://localhost:11434"
    assert settings.ollama_model == "qwen3:4b"
    assert settings.ollama_timeout_seconds == 120.0


def test_settings_read_prefixed_environment_variables(monkeypatch) -> None:
    monkeypatch.setenv(
        "INCIDENTLENS_QDRANT_URL",
        "http://localhost:6333",
    )
    monkeypatch.setenv(
        "INCIDENTLENS_OLLAMA_MODEL",
        "qwen3:1.7b",
    )

    settings = Settings(_env_file=None)

    assert settings.qdrant_url == "http://localhost:6333"
    assert settings.ollama_model == "qwen3:1.7b"


@pytest.mark.parametrize("timeout", [0.0, -1.0])
def test_settings_reject_non_positive_ollama_timeout(timeout: float) -> None:
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            ollama_timeout_seconds=timeout,
        )


def test_settings_reject_unsupported_environment() -> None:
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            environment="prodution",
        )


def test_get_settings_reuses_first_loaded_configuration(
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("INCIDENTLENS_OLLAMA_MODEL", "qwen3:1.7b")

    get_settings = config.get_settings
    get_settings.cache_clear()

    try:
        first_settings = get_settings()

        monkeypatch.setenv("INCIDENTLENS_OLLAMA_MODEL", "qwen3:4b")
        second_settings = get_settings()

        assert second_settings is first_settings
        assert second_settings.ollama_model == "qwen3:1.7b"
    finally:
        get_settings.cache_clear()
