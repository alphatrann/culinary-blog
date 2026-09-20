import asyncio
from dataclasses import dataclass

from culinary_blog.cqrs import Query, QueryHandler
from culinary_blog.health.repository import HealthRepository
from culinary_blog.health.schemas import HealthReport


@dataclass(frozen=True)
class GetReadinessQuery(Query):
    pass


class GetReadinessHandler(QueryHandler[GetReadinessQuery, HealthReport]):
    """Checks only the dependencies required to serve traffic: database and cache."""

    def __init__(self, repository: HealthRepository) -> None:
        self._repository = repository

    async def handle(self, query: GetReadinessQuery) -> HealthReport:
        database, cache = await asyncio.gather(
            self._repository.check_database(),
            self._repository.check_cache_redis(),
        )
        return HealthReport.from_entries({"database": database, "cache_redis": cache})
