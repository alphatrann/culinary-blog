from fastapi import APIRouter

from culinary_blog.cache.redis import get_cache_redis, get_queue_redis, get_ratelimit_redis
from culinary_blog.config import get_settings
from culinary_blog.database.session import engine
from culinary_blog.health.queries.get_health import GetHealthHandler
from culinary_blog.health.queries.get_liveness import GetLivenessHandler
from culinary_blog.health.queries.get_readiness import GetReadinessHandler
from culinary_blog.health.repository import HealthRepository
from culinary_blog.health.router import HealthRouter


def build_health_router() -> APIRouter:
    """Composition root for the health module: the only place that binds concrete dependencies."""
    repository = HealthRepository(
        engine,
        get_cache_redis(),
        get_queue_redis(),
        get_ratelimit_redis(),
        get_settings().minio_health_url,
    )
    return HealthRouter(
        get_health=GetHealthHandler(repository),
        get_liveness=GetLivenessHandler(),
        get_readiness=GetReadinessHandler(repository),
    ).router
