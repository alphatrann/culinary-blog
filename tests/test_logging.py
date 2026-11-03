import asyncio
import json
import logging
import uuid
from collections.abc import Iterator
from io import StringIO
from typing import Annotated
from unittest.mock import AsyncMock

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from culinary_blog.auth.cookies import ACCESS_COOKIE
from culinary_blog.auth.dependencies import Authenticator
from culinary_blog.auth.principal import Principal
from culinary_blog.errors import UnauthorizedError
from culinary_blog.health.queries.get_health import GetHealthHandler
from culinary_blog.health.queries.get_liveness import GetLivenessHandler
from culinary_blog.health.queries.get_readiness import GetReadinessHandler
from culinary_blog.health.repository import HealthRepository
from culinary_blog.health.router import HealthRouter
from culinary_blog.health.schemas import HealthEntry
from culinary_blog.logging import JsonFormatter
from culinary_blog.middleware import CorrelationIdMiddleware
from culinary_blog.problem_details import register_problem_handlers

USER_ID = uuid.UUID("11111111-2222-3333-4444-555555555555")


class FakeTokens:
    """Stands in for TokenService: one known cookie value maps to a principal."""

    def decode_access_token(self, token: str) -> Principal:
        if token != "good":
            raise UnauthorizedError("bad token")
        return Principal(user_id=USER_ID, roles=("author",))


def make_app() -> FastAPI:
    authenticator = Authenticator(FakeTokens())  # type: ignore[arg-type]
    repository = AsyncMock(spec=HealthRepository)
    for name in ("database", "cache_redis", "queue_redis", "ratelimit_redis", "minio"):
        getattr(repository, f"check_{name}").return_value = HealthEntry(status="healthy")

    app = FastAPI()
    register_problem_handlers(app)
    app.include_router(
        HealthRouter(
            get_health=GetHealthHandler(repository),
            get_liveness=GetLivenessHandler(),
            get_readiness=GetReadinessHandler(repository),
        ).router
    )

    @app.get("/slow")
    async def slow() -> dict[str, str]:
        await asyncio.sleep(0.55)
        return {"status": "slow"}

    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("boom")

    @app.get("/me")
    async def me(principal: Annotated[Principal, Depends(authenticator.require_principal)]) -> dict[str, str]:
        return {"user_id": str(principal.user_id)}

    app.add_middleware(CorrelationIdMiddleware)
    return app


@pytest.fixture
def log_lines() -> Iterator[StringIO]:
    """Captures what the JSON handler would print to stdout, one line per record."""
    buffer = StringIO()
    handler = logging.StreamHandler(buffer)
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("culinary_blog")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    yield buffer
    logger.removeHandler(handler)
    logger.setLevel(logging.NOTSET)


def request_entries(buffer: StringIO) -> list[dict]:
    entries = [json.loads(line) for line in buffer.getvalue().splitlines()]
    return [entry for entry in entries if entry["logger"] == "culinary_blog.request"]


def test_correlation_id_from_request_is_echoed_and_logged(log_lines: StringIO) -> None:
    response = TestClient(make_app()).get("/me", headers={"X-Correlation-ID": "abc-123"})
    assert response.headers["X-Correlation-ID"] == "abc-123"
    entry = request_entries(log_lines)[-1]
    assert entry["correlation_id"] == "abc-123"
    assert entry["request_path"] == "/me"


def test_correlation_id_is_generated_when_absent(log_lines: StringIO) -> None:
    response = TestClient(make_app()).get("/me")
    generated = response.headers["X-Correlation-ID"]
    assert len(generated) == 32
    assert request_entries(log_lines)[-1]["correlation_id"] == generated


def test_unsafe_incoming_correlation_id_is_replaced(log_lines: StringIO) -> None:
    response = TestClient(make_app()).get("/me", headers={"X-Correlation-ID": "bad id\nwith newline"})
    assert response.headers["X-Correlation-ID"] != "bad id\nwith newline"
    assert len(response.headers["X-Correlation-ID"]) == 32


def test_request_log_has_route_template_status_and_user_id(log_lines: StringIO) -> None:
    TestClient(make_app()).get("/me", cookies={ACCESS_COOKIE: "good"})
    entry = request_entries(log_lines)[-1]
    assert entry["method"] == "GET"
    assert entry["route"] == "/me"
    assert entry["status"] == 200
    assert entry["level"] == "INFO"
    assert entry["user_id"] == str(USER_ID)
    assert entry["duration_ms"] >= 0


def test_anonymous_request_has_no_user_id(log_lines: StringIO) -> None:
    TestClient(make_app()).get("/me", cookies={ACCESS_COOKIE: "forged"})
    entry = request_entries(log_lines)[-1]
    assert "user_id" not in entry
    assert entry["status"] == 401


def test_slow_request_logs_warning(log_lines: StringIO) -> None:
    TestClient(make_app()).get("/slow")
    entry = request_entries(log_lines)[-1]
    assert entry["level"] == "WARNING"
    assert entry["duration_ms"] > 500
    assert entry["route"] == "/slow"


def test_server_error_logs_error_with_status_500(log_lines: StringIO) -> None:
    client = TestClient(make_app(), raise_server_exceptions=False)
    assert client.get("/boom").status_code == 500
    entry = request_entries(log_lines)[-1]
    assert entry["level"] == "ERROR"
    assert entry["status"] == 500
    assert entry["route"] == "/boom"


@pytest.mark.parametrize("path", ["/health", "/health/live", "/health/ready"])
def test_health_endpoints_are_not_request_logged(log_lines: StringIO, path: str) -> None:
    response = TestClient(make_app()).get(path, headers={"X-Correlation-ID": "probe-1"})
    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"] == "probe-1"
    assert request_entries(log_lines) == []
