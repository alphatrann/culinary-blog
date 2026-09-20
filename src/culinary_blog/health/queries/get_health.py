import asyncio
from dataclasses import dataclass

from culinary_blog.cqrs import Query, QueryHandler
from culinary_blog.health.repository import HealthRepository
from culinary_blog.health.schemas import HealthReport


@dataclass(frozen=True)
class GetHealthQuery(Query):
    pass


class GetHealthHandler(QueryHandler[GetHealthQuery, HealthReport]):
    """Checks every dependency: database, the three Redis instances, and MinIO."""

    def __init__(self, repository: HealthRepository) -> None:
        self._repository = repository

    async def handle(self, query: GetHealthQuery) -> HealthReport:
        database, cache, queue, ratelimit, minio = await asyncio.gather(
            self._repository.check_database(),
            self._repository.check_cache_redis(),
            self._repository.check_queue_redis(),
            self._repository.check_ratelimit_redis(),
            self._repository.check_minio(),
        )
        return HealthReport.from_entries(
            {
                "database": database,
                "cache_redis": cache,
                "queue_redis": queue,
                "ratelimit_redis": ratelimit,
                "minio": minio,
            }
        )
