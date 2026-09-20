from dataclasses import dataclass

from culinary_blog.cqrs import Query, QueryHandler
from culinary_blog.health.schemas import HealthReport


@dataclass(frozen=True)
class GetLivenessQuery(Query):
    pass


class GetLivenessHandler(QueryHandler[GetLivenessQuery, HealthReport]):
    """Process-only check: answers healthy as long as the app can respond at all."""

    async def handle(self, query: GetLivenessQuery) -> HealthReport:
        return HealthReport.from_entries({})
