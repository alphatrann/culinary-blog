"""Cron (FR-JOB-003): enqueues the daily sitemap job at 02:00 UTC. Run exactly one replica or jobs double up.

Run: uv run culinary-blog-cron
"""

import asyncio
import logging
from datetime import UTC, datetime, timedelta

from culinary_blog.cache.redis import get_queue_redis
from culinary_blog.jobs.queue import SITEMAP, RedisJobQueue
from culinary_blog.logging import configure_logging

logger = logging.getLogger(__name__)
RUN_HOUR_UTC = 2


def seconds_until_next_run(now: datetime, hour: int = RUN_HOUR_UTC) -> float:
    """Seconds from `now` (aware) to the next `hour`:00 UTC. Exactly on the hour counts as already run today."""
    now = now.astimezone(UTC)
    target = now.replace(hour=hour, minute=0, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()


async def run_forever() -> None:
    queue = RedisJobQueue(get_queue_redis())
    while True:
        await asyncio.sleep(seconds_until_next_run(datetime.now(UTC)))
        try:
            await queue.enqueue(SITEMAP, {})
            logger.info("enqueued daily sitemap job")
        except Exception:  # a Redis blip must not kill the loop; the next run is a day away anyway
            logger.exception("failed to enqueue daily sitemap job")


def main() -> None:
    configure_logging()
    asyncio.run(run_forever())


if __name__ == "__main__":
    main()
