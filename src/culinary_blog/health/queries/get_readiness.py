from dataclasses import dataclass

from culinary_blog.cqrs import Query, QueryHandler
from culinary_blog.health.repository import HealthRepository
from culinary_blog.health.schemas import HealthReport


@dataclass(frozen=True)
class GetReadinessQuery(Query):
    pass


class GetReadinessHandler(QueryHandler[GetReadinessQuery, HealthReport]):
    """Checks only what is required to serve traffic: the database.

    Cache Redis is deliberately not gating: when it is down, queries fall back to the database (NFR-REL-002), so pulling
    the instance out of rotation would turn a degradation into an outage. Rate Limit Redis is fail-open likewise.
    """

    def __init__(self, repository: HealthRepository) -> None:
        self._repository = repository

    async def handle(self, query: GetReadinessQuery) -> HealthReport:
        return HealthReport.from_entries({"database": await self._repository.check_database()})
