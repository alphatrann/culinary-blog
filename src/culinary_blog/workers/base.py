"""Shared job loop for standalone workers (FR-JOB-001): BRPOP one of the handled queues, run it, retry or dead-letter.

Retries are not slept in-process. A failed job is re-pushed with `run_at` in the future. A worker that pops a job
whose `run_at` is still ahead re-pushes it to the back of the line without counting an attempt, and idles briefly.
A long backoff therefore never blocks other jobs.
"""

import asyncio
import json
import logging
import time
from collections.abc import Awaitable, Callable, Sequence

from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from culinary_blog.jobs.queue import dead_letter_queue

logger = logging.getLogger(__name__)

Handler = Callable[[dict], Awaitable[None]]

# Must stay below the Redis client's socket timeout (redis-py default: 5 s), or every idle BRPOP would raise.
POLL_TIMEOUT_SECONDS = 2
RECONNECT_DELAY_SECONDS = 1
NOT_DUE_IDLE_SECONDS = 1


class JobWorker:
    # Subclasses set these. backoff[i] is the delay before attempt i+2, so len(backoff) == max_attempts - 1.
    backoff: Sequence[int] = ()
    max_attempts: int = 1

    def __init__(
        self,
        redis: Redis,
        handlers: dict[str, Handler],
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self._redis = redis
        self._handlers = handlers
        self._sleep = sleep

    async def run(self) -> None:
        logger.info("worker started: %s", ",".join(self._handlers))
        while True:
            try:
                popped = await self._redis.brpop(list(self._handlers), timeout=POLL_TIMEOUT_SECONDS)  # type: ignore[misc]
            except (RedisConnectionError, RedisTimeoutError):  # Redis restarting or briefly unreachable: keep polling
                logger.warning("job queue unavailable, retrying", exc_info=True)
                await self._sleep(RECONNECT_DELAY_SECONDS)
                continue
            if popped is None:
                continue
            queue, raw = popped
            await self.process(queue.decode() if isinstance(queue, bytes) else queue, raw)

    async def process(self, queue: str, raw: bytes | str) -> None:
        """Run one job; on failure re-enqueue it with a delay, or dead-letter it once attempts are exhausted."""
        payload = json.loads(raw)
        if payload.get("run_at", 0) > time.time():  # not due yet: back of the line, no attempt used
            await self._redis.lpush(queue, json.dumps(payload))  # type: ignore[misc]
            await self._sleep(NOT_DUE_IDLE_SECONDS)
            return
        logger.info("job started: %s attempt %d", queue, payload.get("attempts", 0) + 1)  # payload may hold PII
        try:
            await self._handlers[queue](payload)
            logger.info("job done: %s", queue)
        except Exception:
            attempts = payload.get("attempts", 0) + 1
            logger.exception("job failed: %s (attempt %d/%d)", queue, attempts, self.max_attempts)
            if attempts < self.max_attempts:
                job = {**payload, "attempts": attempts, "run_at": time.time() + self.backoff[attempts - 1]}
                await self._redis.lpush(queue, json.dumps(job))  # type: ignore[misc]
            else:
                dead = {**payload, "attempts": attempts}
                await self._redis.lpush(dead_letter_queue(queue), json.dumps(dead))  # type: ignore[misc]
