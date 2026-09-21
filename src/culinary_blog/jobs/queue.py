import json
from abc import ABC, abstractmethod

from redis.asyncio import Redis

RESIZE_IMAGE = "resize_image"
DELETE_FILE = "delete_file"


def dead_letter_queue(queue: str) -> str:
    return f"{queue}:dlq"


class JobQueue(ABC):
    """Fire-and-forget job producer (ADR-0002). One queue per job type, consumed by standalone workers."""

    @abstractmethod
    async def enqueue(self, queue: str, payload: dict[str, object]) -> None: ...


class RedisJobQueue(JobQueue):
    """Job Queue Redis (ADR-0004): `LPUSH` here, `BRPOP` in the worker, so jobs are FIFO."""

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def enqueue(self, queue: str, payload: dict[str, object]) -> None:
        await self._redis.lpush(queue, json.dumps({**payload, "attempts": 0}))  # type: ignore[misc]
