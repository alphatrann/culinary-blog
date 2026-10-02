"""RedisCache against a real Redis: stampede protection and SWR across independent "workers" (ADR-0005).

Needs a Redis you don't mind a `FLUSHDB` on: set TEST_REDIS_URL, e.g.
    docker run --rm -d -p 6391:6379 redis:7-alpine && export TEST_REDIS_URL=redis://localhost:6391/15
Skipped when the variable is unset; when it is set but unreachable the tests fail (so CI can't silently skip them).
Each "worker" below has its own client and `RedisCache`, like separate uvicorn processes, so the only thing they share
is Redis.
"""

import asyncio
import os
import time

import pytest
from pydantic import BaseModel
from redis.asyncio import Redis

from culinary_blog.cache.service import GENERATION_KEY, RedisCache

REDIS_URL = os.environ.get("TEST_REDIS_URL")
WORKERS = 4

pytestmark = pytest.mark.skipif(REDIS_URL is None, reason="TEST_REDIS_URL not set")


class Thing(BaseModel):
    value: int


class Loader:
    """Counts calls; each call returns the next integer, so stale vs fresh reads are distinguishable."""

    def __init__(self, delay: float = 0.0) -> None:
        self.calls = 0
        self.delay = delay

    async def __call__(self) -> Thing:
        self.calls += 1
        number = self.calls
        if self.delay:
            await asyncio.sleep(self.delay)
        return Thing(value=number)


@pytest.fixture
async def redis():
    client = Redis.from_url(REDIS_URL)
    await client.ping()  # an unreachable TEST_REDIS_URL is a failure, not a skip
    await client.flushdb()
    yield client
    await client.flushdb()
    await client.aclose()


@pytest.fixture
async def make_cache():
    """Factory for independent workers: own connection pool, own RedisCache, shared Redis."""
    clients: list[Redis] = []
    caches: list[RedisCache] = []

    def build(**options) -> RedisCache:
        client = Redis.from_url(REDIS_URL)
        clients.append(client)
        cache = RedisCache(client, **options)
        caches.append(cache)
        return cache

    build.caches = caches  # type: ignore[attr-defined]
    yield build
    for cache in caches:
        await asyncio.gather(*cache._background, return_exceptions=True)
    for client in clients:
        await client.aclose()


async def settle(caches: list[RedisCache]) -> None:
    """Wait for in-flight background revalidations."""
    await asyncio.gather(*(task for cache in caches for task in cache._background))


# --- stampede on a cold key -----------------------------------------------------------------------------------------


@pytest.mark.anyio
async def test_cold_key_stampede_across_workers_hits_the_database_once(redis, make_cache):
    workers = [make_cache(load_wait_seconds=3.0, poll_interval_seconds=0.01) for _ in range(WORKERS)]
    loader = Loader(delay=0.3)

    results = await asyncio.gather(
        *(workers[i % WORKERS].get_or_load_swr("recipe:pho", 1800, Thing, loader) for i in range(80))
    )

    assert loader.calls == 1
    assert {r.value for r in results} == {1}
    assert await redis.exists("lock:recipe:pho") == 0  # the winner released the lock
    assert 0 < await redis.ttl("recipe:pho") <= 1800


@pytest.mark.anyio
async def test_a_crashed_lock_holder_cannot_block_the_key_forever(redis, make_cache):
    cache = make_cache(load_wait_seconds=0.6, poll_interval_seconds=0.01)
    await redis.set("lock:recipe:pho", "dead-worker", px=300)  # held by a process that will never finish
    loader = Loader()

    started = time.monotonic()
    first = await cache.get_or_load_swr("recipe:pho", 1800, Thing, loader)
    waited = time.monotonic() - started

    assert first == Thing(value=1) and 0.5 < waited < 1.5  # gave up waiting, read the database
    assert await redis.get("recipe:pho") is None  # a fallback read doesn't write

    await asyncio.sleep(0.1)  # the dead holder's lock has now expired (its TTL, not a release)
    await cache.get_or_load_swr("recipe:pho", 1800, Thing, loader)
    assert await redis.get("recipe:pho") is not None  # the next reader acquired the lock and populated


@pytest.mark.anyio
async def test_lock_release_only_removes_the_callers_own_lock(redis, make_cache):
    """A's lock expires mid-load and B takes over; A finishing must not delete B's lock."""
    a = make_cache(load_lock_ms=100)
    b = make_cache(load_lock_ms=5000, load_wait_seconds=0.01)

    slow_a = asyncio.create_task(a.get_or_load_swr("recipe:pho", 1800, Thing, Loader(delay=0.4)))
    await asyncio.sleep(0.2)  # A's 100 ms lock has expired; A is still loading
    slow_b = asyncio.create_task(b.get_or_load_swr("recipe:pho", 1800, Thing, Loader(delay=0.8)))
    await asyncio.sleep(0.05)
    assert await redis.exists("lock:recipe:pho") == 1  # B holds it

    await slow_a  # A finishes and "releases"
    assert await redis.exists("lock:recipe:pho") == 1  # ...but B's lock survived

    await slow_b
    assert await redis.exists("lock:recipe:pho") == 0


# --- stale-while-revalidate -----------------------------------------------------------------------------------------


@pytest.mark.anyio
async def test_stale_entry_is_served_without_waiting_and_refreshed_exactly_once_across_workers(redis, make_cache):
    workers = [make_cache(soft_ttl_ratio=0.0) for _ in range(WORKERS)]  # entries are born soft-expired
    await workers[0].get_or_load_swr("recipe:pho", 1800, Thing, Loader())  # populate: value 1
    refresh = Loader(delay=0.4)
    refresh.calls = 1  # so the refreshed value is 2

    async def read(i: int) -> tuple[Thing, float]:
        started = time.monotonic()
        value = await workers[i % WORKERS].get_or_load_swr("recipe:pho", 1800, Thing, refresh)
        return value, time.monotonic() - started

    outcomes = await asyncio.gather(*(read(i) for i in range(80)))

    assert {value.value for value, _ in outcomes} == {1}  # everyone got the stale value...
    assert max(elapsed for _, elapsed in outcomes) < 0.3  # ...without waiting for the 0.4 s refresh
    await settle(workers)
    assert refresh.calls == 2  # exactly one refresh in the whole fleet (1 pre-set + 1)
    assert (await workers[1].get_or_load_swr("recipe:pho", 1800, Thing, Loader())).value == 2


@pytest.mark.anyio
async def test_real_expiry_drives_the_whole_lifecycle_fresh_stale_expired(redis, make_cache):
    cache = make_cache(soft_ttl_ratio=0.3, load_wait_seconds=1.0)  # TTL 1 s: soft at 0.3 s, hard at 1 s
    loader = Loader()

    assert (await cache.get_or_load_swr("recipe:pho", 1, Thing, loader)).value == 1  # miss -> populate
    assert (await cache.get_or_load_swr("recipe:pho", 1, Thing, loader)).value == 1  # fresh hit
    assert loader.calls == 1

    await asyncio.sleep(0.4)  # past the soft expiry, inside the hard TTL
    assert (await cache.get_or_load_swr("recipe:pho", 1, Thing, loader)).value == 1  # stale served immediately
    await settle([cache])
    assert loader.calls == 2
    assert (await cache.get_or_load_swr("recipe:pho", 1, Thing, loader)).value == 2  # refreshed, fresh again

    await asyncio.sleep(1.2)  # past the hard TTL: Redis has dropped the key
    assert await redis.exists("recipe:pho") == 0
    assert (await cache.get_or_load_swr("recipe:pho", 1, Thing, loader)).value == 3  # back on the mutex path


@pytest.mark.anyio
async def test_revalidation_flag_expires_so_a_failed_refresh_is_retried(redis, make_cache):
    cache = make_cache(soft_ttl_ratio=0.0, revalidate_lock_ms=150)
    await cache.get_or_load_swr("recipe:pho", 1800, Thing, Loader())

    async def broken() -> Thing:
        raise RuntimeError("db down")

    await cache.get_or_load_swr("recipe:pho", 1800, Thing, broken)  # stale served, refresh starts and fails
    await settle([cache])
    assert (await cache.get_or_load_swr("recipe:pho", 1800, Thing, broken)).value == 1  # flag still held: no retry yet
    assert not cache._background

    await asyncio.sleep(0.2)  # the flag's TTL has passed
    recovering = Loader()
    recovering.calls = 1
    assert (await cache.get_or_load_swr("recipe:pho", 1800, Thing, recovering)).value == 1  # still stale to the reader
    await settle([cache])
    assert (await cache.get_or_load_swr("recipe:pho", 1800, Thing, Loader())).value == 2  # but a retry did refresh it


@pytest.mark.anyio
async def test_delete_makes_the_next_read_a_miss_even_for_a_soft_stale_entry(redis, make_cache):
    cache = make_cache(soft_ttl_ratio=0.0)
    loader = Loader()
    await cache.get_or_load_swr("recipe:pho", 1800, Thing, loader)

    await cache.delete("recipe:pho")

    assert (await cache.get_or_load_swr("recipe:pho", 1800, Thing, loader)).value == 2  # loaded, not served stale


# --- versioned keys (Lua) -------------------------------------------------------------------------------------------


@pytest.mark.anyio
async def test_first_reads_race_to_seed_one_generation(redis, make_cache):
    workers = [make_cache() for _ in range(WORKERS)]

    await asyncio.gather(
        *(workers[i % WORKERS].get_or_load_versioned("search", f"q{i % 5}", 60, Thing, Loader()) for i in range(60))
    )

    generation = (await redis.get(GENERATION_KEY)).decode()
    prefixes = {key.decode().split(":")[1] for key in await redis.keys("search:v*")}
    assert prefixes == {f"v{generation}"}  # every worker wrote under the one seeded generation


@pytest.mark.anyio
async def test_concurrent_bumps_are_not_lost(redis, make_cache):
    workers = [make_cache() for _ in range(WORKERS)]
    await workers[0].bump_generation()
    before = int(await redis.get(GENERATION_KEY))

    await asyncio.gather(*(workers[i % WORKERS].bump_generation() for i in range(100)))

    assert int(await redis.get(GENERATION_KEY)) == before + 100


@pytest.mark.anyio
async def test_a_load_that_straddles_a_bump_cannot_poison_the_new_generation(redis, make_cache):
    reader, writer = make_cache(), make_cache()

    async def slow_read() -> Thing:
        await asyncio.sleep(0.2)
        return Thing(value=99)  # computed from pre-write data

    in_flight = asyncio.create_task(reader.get_or_load_versioned("recipes:list", "q", 60, Thing, slow_read))
    await asyncio.sleep(0.05)
    await writer.bump_generation()  # a write commits while the read is still running
    await in_flight

    fresh = Loader()
    assert (await writer.get_or_load_versioned("recipes:list", "q", 60, Thing, fresh)).value == 1  # not the stale 99


# --- Redis unreachable ----------------------------------------------------------------------------------------------


@pytest.mark.anyio
async def test_an_unreachable_redis_degrades_to_the_loader_quickly():
    dead = Redis.from_url("redis://127.0.0.1:1/0", socket_connect_timeout=0.2, socket_timeout=0.2)
    cache = RedisCache(dead)
    loader = Loader()

    started = time.monotonic()
    assert (await cache.get_or_load("categories:all", 60, Thing, loader)).value == 1
    assert (await cache.get_or_load_versioned("search", "q", 60, Thing, loader)).value == 2
    assert (await cache.get_or_load_swr("recipe:pho", 60, Thing, loader)).value == 3
    await cache.delete("recipe:pho")
    await cache.bump_generation()

    assert time.monotonic() - started < 3
    await dead.aclose()
