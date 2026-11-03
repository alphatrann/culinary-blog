"""Pure ASGI middleware: correlation id, and one JSON request log line per request (FR-OBS-001, CONS-010)."""

import logging
import re
import time
import uuid

from opentelemetry import trace
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from culinary_blog.logging import correlation_id_var, request_path_var, trace_id_var, user_id_var

CORRELATION_HEADER = "X-Correlation-ID"
SLOW_REQUEST_MS = 500
# Probe traffic would drown the request log; the probes themselves are still answered and echo the header.
UNLOGGED_PATHS = frozenset({"/health", "/health/live", "/health/ready"})
# Client-supplied ids land in logs, so only accept a short token of safe characters (no newlines or spaces).
_VALID_INCOMING_ID = re.compile(r"[A-Za-z0-9._-]{1,128}")

request_logger = logging.getLogger("culinary_blog.request")


class CorrelationIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        correlation_id = self._incoming_id(scope) or uuid.uuid4().hex
        path = scope["path"]
        span_context = trace.get_current_span().get_span_context()
        values = (
            (correlation_id_var, correlation_id),
            (request_path_var, path),
            (user_id_var, None),  # filled in by Authenticator once the principal is resolved
            (trace_id_var, format(span_context.trace_id, "032x") if span_context.is_valid else None),
        )
        tokens = [(var, var.set(value)) for var, value in values]
        status_code = 500  # stays 500 when the app raises; the exception handler then answers with a 500 response
        started = time.perf_counter()

        async def send_with_header(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                message.setdefault("headers", []).append((CORRELATION_HEADER.lower().encode(), correlation_id.encode()))
            await send(message)

        try:
            await self.app(scope, receive, send_with_header)
        finally:
            duration_ms = round((time.perf_counter() - started) * 1000, 1)
            if path not in UNLOGGED_PATHS:
                self._log_request(scope, status_code, duration_ms)
            for var, token in reversed(tokens):
                var.reset(token)

    @staticmethod
    def _incoming_id(scope: Scope) -> str | None:
        for name, value in scope["headers"]:
            if name == b"x-correlation-id":
                candidate = value.decode("latin-1")
                return candidate if _VALID_INCOMING_ID.fullmatch(candidate) else None
        return None

    @staticmethod
    def _log_request(scope: Scope, status_code: int, duration_ms: float) -> None:
        route = scope.get("route")  # set by FastAPI on the shared scope when a route matched
        template = route.path if route is not None else "unmatched"
        if status_code >= 500:
            level = logging.ERROR
        elif duration_ms > SLOW_REQUEST_MS:
            level = logging.WARNING
        else:
            level = logging.INFO
        request_logger.log(
            level,
            "request completed",
            extra={
                "method": scope["method"],
                "route": template,
                "status": status_code,
                "duration_ms": duration_ms,
            },
        )
