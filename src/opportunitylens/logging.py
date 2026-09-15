import re

import structlog
from structlog.typing import EventDict, WrappedLogger

from opportunitylens.config import Settings

_SENSITIVE_KEY_PATTERN = re.compile(
    r"resume_text|email|phone|authorization|cookie|token",
    re.IGNORECASE,
)
_REDACTED = "[REDACTED]"


def _redact_sensitive_values(
    _logger: WrappedLogger,
    _method_name: str,
    event_dict: EventDict,
) -> EventDict:
    return {
        key: _REDACTED if _SENSITIVE_KEY_PATTERN.search(key) else value
        for key, value in event_dict.items()
    }


def configure_logging(settings: Settings) -> None:
    """Configure JSON logs with sensitive values removed by key name."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            _redact_sensitive_values,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(settings.log_level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )
