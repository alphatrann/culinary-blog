from unittest.mock import AsyncMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from culinary_blog.health.queries.get_health import GetHealthHandler
from culinary_blog.health.queries.get_liveness import GetLivenessHandler
from culinary_blog.health.queries.get_readiness import GetReadinessHandler
from culinary_blog.health.repository import HealthRepository
from culinary_blog.health.router import HealthRouter
from culinary_blog.health.schemas import HealthEntry

HEALTHY = HealthEntry(status="healthy")
UNHEALTHY = HealthEntry(status="unhealthy", detail="down")


def make_client(**overrides: HealthEntry) -> TestClient:
    repository = AsyncMock(spec=HealthRepository)
    for name in ("database", "queue_redis", "ratelimit_redis", "minio"):
        getattr(repository, f"check_{name}").return_value = overrides.get(name, HEALTHY)
    app = FastAPI()
    app.include_router(
        HealthRouter(
            get_health=GetHealthHandler(repository),
            get_liveness=GetLivenessHandler(),
            get_readiness=GetReadinessHandler(repository),
        ).router
    )
    return TestClient(app)


def test_health_all_healthy_returns_200():
    response = make_client().get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert set(response.json()["entries"]) == {"database", "queue_redis", "ratelimit_redis", "minio"}


def test_health_any_unhealthy_returns_503():
    response = make_client(minio=UNHEALTHY).get("/health")
    assert response.status_code == 503
    assert response.json()["entries"]["minio"]["detail"] == "down"


def test_liveness_ignores_dependencies():
    assert make_client(database=UNHEALTHY).get("/health/live").status_code == 200


def test_readiness_only_checks_database():
    others = {"minio": UNHEALTHY, "queue_redis": UNHEALTHY, "ratelimit_redis": UNHEALTHY}
    assert make_client(**others).get("/health/ready").status_code == 200
    assert make_client(database=UNHEALTHY).get("/health/ready").status_code == 503


def test_cache_redis_is_not_probed():
    response = make_client().get("/health")
    assert "cache_redis" not in response.json()["entries"]
