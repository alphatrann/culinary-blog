"""Structured JSON logging (CONS-010, FR-OBS-001). Stdlib only; the OTel handler is attached in main.py."""

import contextvars
import json
import logging
import sys
from datetime import UTC, datetime

correlation_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("correlation_id", default=None)
request_path_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_path", default=None)
user_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("user_id", default=None)
trace_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("trace_id", default=None)

_CONTEXT_VARS = {
    "correlation_id": correlation_id_var,
    "request_path": request_path_var,
    "user_id": user_id_var,
    "trace_id": trace_id_var,
}
# Attributes every LogRecord has. Anything else arrived via `extra=` and is copied into the JSON line.
_RESERVED = set(vars(logging.makeLogRecord({}))) | {"message", "asctime", "exc_text", "stack_info"}


class JsonFormatter(logging.Formatter):
    """One JSON object per line. Context vars are read at format time, so format in the emitting task."""

    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, var in _CONTEXT_VARS.items():
            if (value := var.get()) is not None:
                entry[key] = value
        for key, value in vars(record).items():
            if key not in _RESERVED and key not in entry:
                entry[key] = value
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str)


def configure_logging(level: int = logging.INFO) -> None:
    """Replace root handlers with a single stdout JSON handler. Safe to call more than once."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)
