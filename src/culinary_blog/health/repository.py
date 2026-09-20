import httpx
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from culinary_blog.health.schemas import HealthEntry


class HealthRepository:
    """Probes each infrastructure dependency. Probes never raise; failures become unhealthy entries."""

    def __init__(
        self,
        engine: AsyncEngine,
        cache_redis: Redis,
        queue_redis: Redis,
        ratelimit_redis: Redis,
        minio_health_url: str,
    ) -> None:
        self._engine = engine
        self._cache_redis = cache_redis
        self._queue_redis = queue_redis
        self._ratelimit_redis = ratelimit_redis
        self._minio_health_url = minio_health_url

    async def check_database(self) -> HealthEntry:
        try:
            async with self._engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
            return HealthEntry(status="healthy")
        except Exception as exc:  # noqa: BLE001 - health checks must never raise
            return HealthEntry(status="unhealthy", detail=str(exc))

    async def check_cache_redis(self) -> HealthEntry:
        return await self._ping(self._cache_redis)

    async def check_queue_redis(self) -> HealthEntry:
        return await self._ping(self._queue_redis)

    async def check_ratelimit_redis(self) -> HealthEntry:
        return await self._ping(self._ratelimit_redis)

    async def check_minio(self) -> HealthEntry:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(self._minio_health_url)
            if response.status_code == 200:
                return HealthEntry(status="healthy")
            return HealthEntry(status="unhealthy", detail=f"HTTP {response.status_code}")
        except Exception as exc:  # noqa: BLE001
            return HealthEntry(status="unhealthy", detail=str(exc))

    @staticmethod
    async def _ping(client: Redis) -> HealthEntry:
        try:
            await client.ping()
            return HealthEntry(status="healthy")
        except Exception as exc:  # noqa: BLE001
            return HealthEntry(status="unhealthy", detail=str(exc))
