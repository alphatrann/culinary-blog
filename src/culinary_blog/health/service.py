import asyncio

import httpx
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from culinary_blog.config import get_settings
from culinary_blog.health.schemas import HealthEntry, HealthReport

settings = get_settings()


async def _check_database(engine: AsyncEngine) -> HealthEntry:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return HealthEntry(status="healthy")
    except Exception as exc:  # noqa: BLE001 - health checks must never raise
        return HealthEntry(status="unhealthy", detail=str(exc))


async def _check_redis(client: Redis) -> HealthEntry:
    try:
        await client.ping()
        return HealthEntry(status="healthy")
    except Exception as exc:  # noqa: BLE001
        return HealthEntry(status="unhealthy", detail=str(exc))


async def _check_minio() -> HealthEntry:
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(settings.minio_health_url)
        if response.status_code == 200:
            return HealthEntry(status="healthy")
        return HealthEntry(status="unhealthy", detail=f"HTTP {response.status_code}")
    except Exception as exc:  # noqa: BLE001
        return HealthEntry(status="unhealthy", detail=str(exc))


def _aggregate(entries: dict[str, HealthEntry]) -> HealthReport:
    overall = "healthy" if all(entry.status == "healthy" for entry in entries.values()) else "unhealthy"
    return HealthReport(status=overall, entries=entries)


async def get_full_health(
    engine: AsyncEngine, cache_redis: Redis, queue_redis: Redis, ratelimit_redis: Redis
) -> HealthReport:
    database, cache, queue, ratelimit, minio = await asyncio.gather(
        _check_database(engine),
        _check_redis(cache_redis),
        _check_redis(queue_redis),
        _check_redis(ratelimit_redis),
        _check_minio(),
    )
    return _aggregate(
        {
            "database": database,
            "cache_redis": cache,
            "queue_redis": queue,
            "ratelimit_redis": ratelimit,
            "minio": minio,
        }
    )


async def get_readiness(engine: AsyncEngine, cache_redis: Redis) -> HealthReport:
    database, cache = await asyncio.gather(_check_database(engine), _check_redis(cache_redis))
    return _aggregate({"database": database, "cache_redis": cache})
