from fastapi import APIRouter, Response

from culinary_blog.health.queries.get_health import GetHealthHandler, GetHealthQuery
from culinary_blog.health.queries.get_liveness import GetLivenessHandler, GetLivenessQuery
from culinary_blog.health.queries.get_readiness import GetReadinessHandler, GetReadinessQuery
from culinary_blog.health.schemas import HealthReport


class HealthRouter:
    """HTTP adapter for the health queries. Only maps the report status to an HTTP status code."""

    def __init__(
        self,
        get_health: GetHealthHandler,
        get_liveness: GetLivenessHandler,
        get_readiness: GetReadinessHandler,
    ) -> None:
        self._get_health = get_health
        self._get_liveness = get_liveness
        self._get_readiness = get_readiness
        self.router = APIRouter(tags=["health"])
        self.router.add_api_route("/health", self.health, methods=["GET"], response_model=HealthReport)
        self.router.add_api_route("/health/live", self.live, methods=["GET"], response_model=HealthReport)
        self.router.add_api_route("/health/ready", self.ready, methods=["GET"], response_model=HealthReport)

    async def health(self, response: Response) -> HealthReport:
        return self._with_status(await self._get_health.handle(GetHealthQuery()), response)

    async def live(self) -> HealthReport:
        return await self._get_liveness.handle(GetLivenessQuery())

    async def ready(self, response: Response) -> HealthReport:
        return self._with_status(await self._get_readiness.handle(GetReadinessQuery()), response)

    @staticmethod
    def _with_status(report: HealthReport, response: Response) -> HealthReport:
        if report.status == "unhealthy":
            response.status_code = 503
        return report
