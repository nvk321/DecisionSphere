"""
Tests for Structured Logging & Secret Redaction.
"""
import json
import logging

from backend.app.core.logging import (
    PlainStructuredFormatter,
    StructuredJsonFormatter,
    get_request_id,
    redact_sensitive_text,
    set_request_id,
)


def test_request_id_contextvar_propagation():
    """Verify correlation ID sets and retrieves properly in async context."""
    assert get_request_id() is None
    token = set_request_id("req-test-12345")
    assert get_request_id() == "req-test-12345"
    set_request_id(None)
    assert get_request_id() is None


def test_structured_json_formatter():
    """Verify StructuredJsonFormatter outputs valid JSON with expected fields."""
    formatter = StructuredJsonFormatter()
    set_request_id("req-json-audit-01")

    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=42,
        msg="Scenario simulation executed successfully",
        args=(),
        exc_info=None,
    )

    formatted_str = formatter.format(record)
    parsed = json.loads(formatted_str)

    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "test.logger"
    assert parsed["message"] == "Scenario simulation executed successfully"
    assert parsed["request_id"] == "req-json-audit-01"
    assert "timestamp" in parsed
    assert parsed["line_no"] == 42

    set_request_id(None)


def test_plain_structured_formatter():
    """Verify PlainStructuredFormatter formats human-readable string."""
    formatter = PlainStructuredFormatter()
    set_request_id("req-plain-01")

    record = logging.LogRecord(
        name="test.logger",
        level=logging.WARNING,
        pathname=__file__,
        lineno=100,
        msg="Risk threshold elevated",
        args=(),
        exc_info=None,
    )

    formatted_str = formatter.format(record)
    assert "[WARNING]" in formatted_str
    assert "[req-plain-01]" in formatted_str
    assert "Risk threshold elevated" in formatted_str

    set_request_id(None)


def test_sensitive_credential_redaction():
    """Verify automatic masking of secrets and tokens in log messages."""
    raw_message = "Connecting to postgres with password=mySecretPassword123 and api_key=ak_live_xyz999"
    redacted = redact_sensitive_text(raw_message)

    assert "mySecretPassword123" not in redacted
    assert "ak_live_xyz999" not in redacted
    assert 'password="[REDACTED]"' in redacted
    assert 'api_key="[REDACTED]"' in redacted
