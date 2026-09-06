"""
Structured Application Logging for DecisionSphere.

Enforces JSON-formatted logs with correlation ID tracking, UTC timestamps,
and automatic credential/token redaction.
"""
from __future__ import annotations

import contextvars
from datetime import datetime, timezone
import json
import logging
import re
import sys
from typing import Any, Dict, Optional

# Context variable tracking current correlation ID across async execution flow
request_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id_ctx", default=None
)


def get_request_id() -> Optional[str]:
    """Retrieve the correlation ID of the current request context."""
    return request_id_ctx.get()


def set_request_id(request_id: Optional[str]) -> contextvars.Token[Optional[str]]:
    """Set the correlation ID for the current request context."""
    return request_id_ctx.set(request_id)


REDACTION_PATTERNS = [
    re.compile(r"(password|token|secret|api[_-]?key|credential)[\"']?\s*[:=]\s*[\"']?([^\"'\s,]+)", re.IGNORECASE)
]


def redact_sensitive_text(text: str) -> str:
    """Mask credentials and sensitive parameters in text strings."""
    redacted = text
    for pattern in REDACTION_PATTERNS:
        redacted = pattern.sub(r'\1="[REDACTED]"', redacted)
    return redacted


class StructuredJsonFormatter(logging.Formatter):
    """
    Format log records as structured JSON dictionaries for production observability.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": redact_sensitive_text(record.getMessage()),
            "request_id": get_request_id(),
            "module": record.module,
            "func_name": record.funcName,
            "line_no": record.lineno,
        }

        # Include exception trace if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Include extra dictionary attributes passed via extra={}
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            for k, v in record.extra.items():
                if k not in log_data and not k.startswith("_"):
                    log_data[k] = v

        return json.dumps(log_data, default=str)


class PlainStructuredFormatter(logging.Formatter):
    """
    Human-readable structured console formatter for local interactive debugging.
    """

    def format(self, record: logging.LogRecord) -> str:
        req_id = get_request_id() or "-"
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        msg = redact_sensitive_text(record.getMessage())
        base = f"[{timestamp}] [{record.levelname:<7}] [{req_id}] [{record.name}]: {msg}"
        if record.exc_info:
            base += "\n" + self.formatException(record.exc_info)
        return base


def setup_logging(log_level: str = "INFO", json_format: bool = True) -> None:
    """
    Configure root application logger with structured formatter.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplication
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    if json_format:
        handler.setFormatter(StructuredJsonFormatter())
    else:
        handler.setFormatter(PlainStructuredFormatter())

    root_logger.addHandler(handler)

    # Moderate noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Authoritative logger factory."""
    return logging.getLogger(name)
