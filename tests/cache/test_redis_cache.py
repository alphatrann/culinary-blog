import asyncio

import pytest
from fakeredis import FakeAsyncRedis, FakeServer
from pydantic import BaseModel

from culinary_blog.cache.service import GENERATION_KEY, RedisCache


class Thing(BaseModel):
    value: int


class Loader:
    """Counts calls and hands out an increasing value, so a stale vs. fresh read is visible."""

    def __init__(self, delay: float = 0.0) -> None:
        self.calls = 0
        self.delay = delay

    async def __call__(self) -> Thing:
        self.calls += 1
        if self.delay:
            await asyncio.sleep(self.delay)
        return Thing(value=self.calls)


@pytest.fixture
def server() -> FakeServer:
    return FakeServer()


@pytest.fixture
def redis(server) -> FakeAsyncRedis:
    return FakeAsyncRedis(server=server)


@pytest.fixture
def cache(redis) -> RedisCache:
    return RedisCache(redis, load_wait_seconds=1.0, poll_interval_seconds=0.005)


# --- plain cache-aside ----------------------------------------------------------------------------------------------


@pytest.mark.anyio
async def test_plain_miss_loads_stores_with_ttl_then_hits(cache, redis):
    loader = Loader()

    first = await cache.get_or_load("categories:all", 3600, Thing, loader)
    second = await cache.get_or_load("categories:all", 3600, Thing, loader)

    assert first == second == Thing(value=1)
    assert loader.calls == 1
    assert 0 < await redis.ttl("categories:all") <= 3600


@pytest.mark.anyio
async def test_unreadable_cached_payload_is_treated_as_a_miss(cache, redis):
    await redis.set("categories:all", b"not json")

    out = await cache.get_or_load("categories:all", 60, Thing, Loader())

    assert out == Thing(value=1)


@pytest.mark.anyio
async def test_delete_removes_entries(cache, redis):
    await cache.get_or_load("a", 60, Thing, Loader())

    await cache.delete("a", "missing")

    assert await redis.get("a") is None


# --- versioned keys -------------------------------------------------------------------------------------------------


@pytest.mark.anyio
async def test_versioned_hit_after_miss_and_distinct_queries_do_not_collide(cache):
    loader = Loader()

    await cache.get_or_load_versioned("recipes:list", "q1", 60, Thing, loader)
    again = await cache.get_or_load_versioned("recipes:list", "q1", 60, Thing, loader)
    other = await cache.get_or_load_versioned("recipes:list", "q2", 60, Thing, loader)

    assert again == Thing(value=1)
    assert other == Thing(value=2)
    assert loader.calls == 2


@pytest.mark.anyio
async def test_bump_generation_invalidates_every_versioned_key_in_one_step(cache):
    loader = Loader()
    await cache.get_or_load_versioned("recipes:list", "q1", 60, Thing, loader)
    await cache.get_or_load_versioned("search", "q9", 60, Thing, loader)

    await cache.bump_generation()

    assert await cache.get_or_load_versioned("recipes:list", "q1", 60, Thing, loader) == Thing(value=3)
    assert await cache.get_or_load_versioned("search", "q9", 60, Thing, loader) == Thing(value=4)


@pytest.mark.anyio
async def test_generation_survives_ttl_free_and_is_seeded_so_a_reset_cannot_reuse_an_old_one(cache, redis):
    await cache.get_or_load_versioned("search", "q", 60, Thing, Loader())
    first_generation = await redis.get(GENERATION_KEY)
    assert await redis.ttl(GENERATION_KEY) == -1  # no expiry

    await redis.delete(GENERATION_KEY)  # simulates eviction
    await cache.bump_generation()

    assert int(await redis.get(GENERATION_KEY)) > int(first_generation)


@pytest.mark.anyio
async def test_a_result_loaded_across_a_bump_is_written_to_the_dead_generation(cache):
    """A read that started before an invalidation must not poison the new generation with pre-write data."""

    async def slow_loader() -> Thing:
        await cache.bump_generation()  # a write lands while this read is still in flight
        return Thing(value=99)

    await cache.get_or_load_versioned("recipes:list", "q", 60, Thing, slow_loader)

    fresh = Loader()
    assert await cache.get_or_load_versioned("recipes:list", "q", 60, Thing, fresh) == Thing(value=1)


# --- stale-while-revalidate + mutex (ADR-0005) ----------------------------------------------------------------------


@pytest.mark.anyio
async def test_swr_serves_fresh_entries_without_loading(cache):
    loader = Loader()
    await cache.get_or_load_swr("recipe:pho", 1800, Thing, loader)

    assert await cache.get_or_load_swr("recipe:pho", 1800, Thing, loader) == Thing(value=1)
    assert loader.calls == 1


@pytest.mark.anyio
async def test_swr_cold_key_stampede_hits_the_database_once(cache):
    loader = Loader(delay=0.05)

    results = await asyncio.gather(*(cache.get_or_load_swr("recipe:pho", 1800, Thing, loader) for _ in range(20)))

    assert loader.calls == 1
    assert {r.value for r in results} == {1}


@pytest.mark.anyio
async def test_swr_stale_entry_is_served_immediately_and_refreshed_exactly_once(redis):
    cache = RedisCache(redis, soft_ttl_ratio=0.0)  # every stored entry is born soft-expired
    loader = Loader(delay=0.05)
    await cache.get_or_load_swr("recipe:pho", 1800, Thing, loader)  # populate (call 1)

    results = await asyncio.gather(*(cache.get_or_load_swr("recipe:pho", 1800, Thing, loader) for _ in range(20)))
    assert {r.value for r in results} == {1}  # everyone got the stale value without waiting
    await asyncio.gather(*cache._background)

    assert loader.calls == 2  # populate + exactly one background refresh
    assert (await cache.get_or_load_swr("recipe:pho", 1800, Thing, Loader())).value == 2


@pytest.mark.anyio
async def test_swr_failed_refresh_keeps_serving_the_stale_value(redis):
    cache = RedisCache(redis, soft_ttl_ratio=0.0)
    await cache.get_or_load_swr("recipe:pho", 1800, Thing, Loader())

    async def broken() -> Thing:
        raise RuntimeError("db down")

    assert (await cache.get_or_load_swr("recipe:pho", 1800, Thing, broken)).value == 1
    await asyncio.gather(*cache._background)
    assert (await cache.get_or_load_swr("recipe:pho", 1800, Thing, broken)).value == 1


@pytest.mark.anyio
async def test_swr_waiters_fall_back_to_the_database_when_the_lock_holder_is_too_slow(redis):
    cache = RedisCache(redis, load_wait_seconds=0.05, poll_interval_seconds=0.01)
    await redis.set("lock:recipe:pho", "someone-else", px=5000)  # a loader that never finishes
    loader = Loader()

    assert await cache.get_or_load_swr("recipe:pho", 1800, Thing, loader) == Thing(value=1)
    assert await redis.get("recipe:pho") is None  # a fallback read doesn't write


@pytest.mark.anyio
async def test_swr_releases_the_lock_even_when_the_loader_fails(cache, redis):
    async def broken() -> Thing:
        raise RuntimeError("db down")

    with pytest.raises(RuntimeError):
        await cache.get_or_load_swr("recipe:pho", 1800, Thing, broken)

    assert await redis.get("lock:recipe:pho") is None


@pytest.mark.anyio
async def test_swr_not_found_is_not_cached(cache, redis):
    class Missing(Exception): ...

    async def missing() -> Thing:
        raise Missing

    with pytest.raises(Missing):
        await cache.get_or_load_swr("recipe:nope", 1800, Thing, missing)

    assert await redis.get("recipe:nope") is None


# --- Cache Redis down (NFR-REL-002) ---------------------------------------------------------------------------------


@pytest.mark.anyio
async def test_every_read_path_falls_back_to_the_loader_when_redis_is_down(cache, server):
    server.connected = False
    loader = Loader()

    assert await cache.get_or_load("categories:all", 60, Thing, loader) == Thing(value=1)
    assert await cache.get_or_load_versioned("search", "q", 60, Thing, loader) == Thing(value=2)
    assert await cache.get_or_load_swr("recipe:pho", 60, Thing, loader) == Thing(value=3)


@pytest.mark.anyio
async def test_invalidation_does_not_raise_when_redis_is_down(cache, server):
    server.connected = False

    await cache.delete("recipe:pho")
    await cache.bump_generation()
