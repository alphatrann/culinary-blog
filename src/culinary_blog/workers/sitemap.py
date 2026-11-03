"""Sitemap worker (NFR-SEO-003, FR-JOB-003): consumes `sitemap` jobs from the Job Queue Redis.

Run: uv run culinary-blog-sitemap-worker
Builds the XML, stores it at `sitemap/sitemap.xml`, then pings Google (best effort). Failed jobs are retried once
after 1 min and once after 5 min, then parked in `sitemap:dlq`.
"""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from urllib.parse import urlencode

import httpx
from redis.asyncio import Redis

from culinary_blog.cache.redis import get_queue_redis
from culinary_blog.config import Settings, get_settings
from culinary_blog.jobs.queue import SITEMAP
from culinary_blog.logging import configure_logging
from culinary_blog.sitemap.builder import STORED_KEY
from culinary_blog.sitemap.queries.get_sitemap import GetSitemapHandler
from culinary_blog.sitemap.wiring import build_get_sitemap
from culinary_blog.storage.minio_storage import MinioFileStorage
from culinary_blog.storage.service import FileStorageService
from culinary_blog.workers.base import JobWorker

logger = logging.getLogger(__name__)

GOOGLE_PING_URL = "https://www.google.com/ping"


async def ping_google(sitemap_url: str) -> None:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{GOOGLE_PING_URL}?{urlencode({'sitemap': sitemap_url})}")
        response.raise_for_status()


class SitemapWorker(JobWorker):
    max_attempts = 3  # 1 try + 2 retries
    backoff = (60, 300)

    def __init__(
        self,
        redis: Redis,
        storage: FileStorageService,
        sitemap: GetSitemapHandler,
        settings: Settings,
        ping: Callable[[str], Awaitable[None]] = ping_google,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self._storage = storage
        self._sitemap = sitemap
        self._sitemap_url = settings.site_url.rstrip("/") + "/sitemap.xml"
        self._ping = ping
        super().__init__(redis, {SITEMAP: self._publish}, sleep)

    async def _publish(self, payload: dict) -> None:
        await self._storage.put_at(STORED_KEY, await self._sitemap.build(), "text/xml")
        try:
            await self._ping(self._sitemap_url)
        except Exception:  # best effort: a failed ping must not retry (or dead-letter) an already-stored sitemap
            logger.warning("google sitemap ping failed", exc_info=True)


def main() -> None:
    configure_logging()
    settings = get_settings()
    storage = MinioFileStorage(settings)
    asyncio.run(SitemapWorker(get_queue_redis(), storage, build_get_sitemap(storage), settings).run())


if __name__ == "__main__":
    main()
