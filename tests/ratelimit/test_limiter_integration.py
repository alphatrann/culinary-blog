"""Rate limiters against a real Redis: Lua atomicity under concurrency (ADR-0006).

fakeredis proves the scripts' logic, not that Redis executes each one atomically, so these hammer the limiters from
several independent clients ("API workers", each with its own connection pool) at once. Same gating as
tests/cache/test_redis_cache_integration.py: skipped without TEST_REDIS_URL, fails (not skips) if it is unreachable.
The DB is flushed.
"""

import asyncio
import os
import time

import pytest
from redis.asyncio import BlockingConnectionPool, Redis

from culinary_blog.ratelimit.limiter import SlidingWindowLimiter, TokenBucketLimiter

REDIS_URL = os.environ.get("TEST_REDIS_URL")
WORKERS = 4
LIMIT = 50
REQUESTS = 400
WINDOW = 3600  # long enough that the test sits inside one window (see `away_from_window_edge`)

pytestmark = [pytest.mark.skipif(REDIS_URL is None, reason="TEST_REDIS_URL not set"), pytest.mark.anyio]


@pytest.fixture
async def redis():
    client = Redis.from_url(REDIS_URL)
    await client.ping()
    await client.flushdb()
    yield client
    await client.flushdb()
    await client.aclose()


@pytest.fixture
async def make_client():
    clients: list[Redis] = []

    def build() -> Redis:
        # Bounded pool like a real worker: waiting requests queue on the pool, many still reach Redis concurrently.
        client = Redis(connection_pool=BlockingConnectionPool.from_url(REDIS_URL, max_connections=16))
        clients.append(client)
        return client

    yield build
    for client in clients:
        await client.aclose()


async def away_from_window_edge(redis: Redis, margin: int = 10) -> None:
    """The sliding window weighs the previous window in; don't let a window roll over mid-test."""
    now = int((await redis.time())[0])
    remaining = WINDOW - now % WINDOW
    if remaining < margin:
        await asyncio.sleep(remaining + 1)


async def test_sliding_window_never_over_admits_under_concurrency(redis, make_client) -> None:
    await away_from_window_edge(redis)
    limiters = [SlidingWindowLimiter(make_client(), "auth", LIMIT, WINDOW, WINDOW + 60) for _ in range(WORKERS)]

    results = await asyncio.gather(*(limiters[i % WORKERS].check("same-ip") for i in range(REQUESTS)))

    allowed = [r for r in results if r.allowed]
    assert len(allowed) == LIMIT  # a non-atomic read-then-increment would admit more than LIMIT
    assert all(not r.allowed and r.retry_after >= 1 for r in results if not r.allowed)
    # The counter holds exactly the admitted requests: denied ones must not be counted.
    counters = [int(await redis.get(k)) async for k in redis.scan_iter("ratelimit:auth:same-ip:*")]
    assert counters == [LIMIT]


async def test_sliding_window_concurrent_identifiers_do_not_interfere(redis, make_client) -> None:
    await away_from_window_edge(redis)
    limiter = SlidingWindowLimiter(make_client(), "upload", 5, WINDOW, WINDOW + 60)
    ids = [f"user-{n}" for n in range(20)]

    results = await asyncio.gather(*(limiter.check(i) for i in ids for _ in range(12)))

    per_id = {i: 0 for i in ids}
    for identifier, result in zip((i for i in ids for _ in range(12)), results, strict=True):
        per_id[identifier] += result.allowed
    assert set(per_id.values()) == {5}


async def test_token_bucket_never_over_admits_under_concurrency(redis, make_client) -> None:
    # Refill is LIMIT/3600 per second, so well under one token during the test: exactly LIMIT can pass.
    limiters = [TokenBucketLimiter(make_client(), "api", LIMIT, WINDOW, WINDOW + 60) for _ in range(WORKERS)]

    results = await asyncio.gather(*(limiters[i % WORKERS].check("same-ip") for i in range(REQUESTS)))

    assert sum(r.allowed for r in results) == LIMIT
    assert all(r.retry_after >= 1 for r in results if not r.allowed)


async def test_token_bucket_refills_on_real_redis(redis, make_client) -> None:
    limiter = TokenBucketLimiter(make_client(), "api", 10, 1, 60)  # 10 tokens/second
    assert sum([(await limiter.check("a")).allowed for _ in range(15)]) == 10
    await asyncio.sleep(0.35)  # ~3 tokens back; asserting >= 2 leaves slack for a slow runner
    refilled = sum([(await limiter.check("a")).allowed for _ in range(10)])
    assert 2 <= refilled <= 5


async def test_keys_expire(redis, make_client) -> None:
    window = SlidingWindowLimiter(make_client(), "auth", 5, 60, 90)
    bucket = TokenBucketLimiter(make_client(), "api", 5, 60, 90)
    await window.check("a")
    await bucket.check("a")
    keys = [k async for k in redis.scan_iter("ratelimit:*")]
    assert len(keys) == 2
    for key in keys:
        assert 0 < await redis.ttl(key) <= 90


async def test_fails_open_when_redis_is_unreachable() -> None:
    dead = Redis.from_url("redis://localhost:1/0", socket_timeout=0.2, socket_connect_timeout=0.2)
    started = time.monotonic()
    result = await SlidingWindowLimiter(dead, "auth", 5, 60, 90).check("a")
    assert result.allowed
    assert time.monotonic() - started < 2
    await dead.aclose()
