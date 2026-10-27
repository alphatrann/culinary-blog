import json
import time
from abc import ABC, abstractmethod

from redis.asyncio import Redis

RESIZE_IMAGE = "resize_image"
DELETE_FILE = "delete_file"
WELCOME_EMAIL = "welcome_email"
SITEMAP = "sitemap"


def dead_letter_queue(queue: str) -> str:
    return f"{queue}:dlq"


class JobQueue(ABC):
    """Fire-and-forget job producer (ADR-0002). One queue per job type, consumed by standalone workers."""

    @abstractmethod
    async def enqueue(self, queue: str, payload: dict[str, object], delay_seconds: int = 0) -> None: ...


class RedisJobQueue(JobQueue):
    """Job Queue Redis (ADR-0004): `LPUSH` here, `BRPOP` in the worker, so jobs are FIFO."""

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def enqueue(self, queue: str, payload: dict[str, object], delay_seconds: int = 0) -> None:
        # run_at: the worker holds the job back until this epoch time (see workers/base.py).
        job = {**payload, "attempts": 0, "run_at": time.time() + delay_seconds}
        await self._redis.lpush(queue, json.dumps(job))  # type: ignore[misc]
