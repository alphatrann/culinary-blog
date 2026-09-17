from fastapi import APIRouter, Response

from culinary_blog.cache.redis import get_cache_redis, get_queue_redis, get_ratelimit_redis
from culinary_blog.database.session import engine
from culinary_blog.health import service
from culinary_blog.health.schemas import HealthReport

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthReport)
async def health(response: Response) -> HealthReport:
    report = await service.get_full_health(
        engine, get_cache_redis(), get_queue_redis(), get_ratelimit_redis()
    )
    if report.status == "unhealthy":
        response.status_code = 503
    return report


@router.get("/health/live", response_model=HealthReport)
async def health_live() -> HealthReport:
    return HealthReport(status="healthy", entries={})


@router.get("/health/ready", response_model=HealthReport)
async def health_ready(response: Response) -> HealthReport:
    report = await service.get_readiness(engine, get_cache_redis())
    if report.status == "unhealthy":
        response.status_code = 503
    return report
