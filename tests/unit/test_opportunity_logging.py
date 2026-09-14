import structlog

from opportunitylens.config import Settings
from opportunitylens.logging import configure_logging


def test_structured_logging_redacts_sensitive_keys(capsys) -> None:
    configure_logging(Settings(_env_file=None))

    structlog.get_logger().info(
        "profile received",
        resume_text="private resume text",
        email="person@example.com",
        phone="+65 5555 5555",
        authorization="Bearer secret",
        cookie="session=secret",
        token="secret-token",
        safe_id="profile-1",
    )

    output = capsys.readouterr().out
    assert "private resume text" not in output
    assert "person@example.com" not in output
    assert "+65 5555 5555" not in output
    assert "Bearer secret" not in output
    assert "session=secret" not in output
    assert "secret-token" not in output
    assert '"safe_id": "profile-1"' in output
