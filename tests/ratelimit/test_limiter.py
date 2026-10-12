import pytest
from fakeredis import FakeAsyncRedis, FakeServer
from redis.exceptions import ConnectionError as RedisConnectionError

from culinary_blog.ratelimit.limiter import SlidingWindowLimiter, TokenBucketLimiter

pytestmark = pytest.mark.anyio


@pytest.fixture
def redis() -> FakeAsyncRedis:
    return FakeAsyncRedis(server=FakeServer())


async def test_sliding_window_allows_up_to_limit_then_blocks(redis) -> None:
    limiter = SlidingWindowLimiter(redis, "auth", 3, 60, 90)
    results = [await limiter.check("1.1.1.1") for _ in range(4)]
    assert [r.allowed for r in results[:3]] == [True, True, True]
    assert results[0].remaining >= 1 and results[2].remaining == 0
    blocked = results[3]
    assert not blocked.allowed and 1 <= blocked.retry_after <= 60 and blocked.limit == 3


async def test_sliding_window_isolates_identifiers(redis) -> None:
    limiter = SlidingWindowLimiter(redis, "auth", 1, 60, 90)
    assert (await limiter.check("a")).allowed
    assert not (await limiter.check("a")).allowed
    assert (await limiter.check("b")).allowed


async def test_sliding_window_sets_key_ttl(redis) -> None:
    limiter = SlidingWindowLimiter(redis, "auth", 5, 60, 90)
    await limiter.check("a")
    keys = [k async for k in redis.scan_iter("ratelimit:auth:a:*")]
    assert len(keys) == 1
    assert 0 < await redis.ttl(keys[0]) <= 90


async def test_sliding_window_counts_previous_window(redis) -> None:
    limiter = SlidingWindowLimiter(redis, "auth", 2, 3600, 7200)
    now = int((await redis.time())[0])
    index = now // 3600
    # A full previous hour just ended; at the very start of this hour it still weighs ~100%, so the user is blocked.
    # Mid-hour it weighs less. Either way it can only ever reduce the budget, never exceed the limit.
    await redis.set(f"ratelimit:auth:a:{index - 1}", 2)
    elapsed_fraction = (now % 3600) / 3600
    result = await limiter.check("a")
    assert result.allowed == (2 * (1 - elapsed_fraction) + 1 <= 2)


async def test_token_bucket_allows_burst_then_blocks(redis) -> None:
    limiter = TokenBucketLimiter(redis, "api", 5, 60, 90)
    results = [await limiter.check("a") for _ in range(6)]
    assert [r.allowed for r in results] == [True] * 5 + [False]
    assert results[0].remaining == 4
    assert results[5].retry_after >= 1


async def test_token_bucket_refills_continuously(redis) -> None:
    limiter = TokenBucketLimiter(redis, "api", 60, 60, 90)  # 1 token per second
    for _ in range(60):
        assert (await limiter.check("a")).allowed
    assert not (await limiter.check("a")).allowed
    # Rewind the bucket's clock by 3s -> 3 tokens refilled.
    ts = float(await redis.hget("ratelimit:api:a", "ts"))
    await redis.hset("ratelimit:api:a", "ts", str(ts - 3))
    assert [(await limiter.check("a")).allowed for _ in range(4)] == [True, True, True, False]


class BrokenRedis:
    async def eval(self, *args, **kwargs):
        raise RedisConnectionError("down")


@pytest.mark.parametrize("cls", [SlidingWindowLimiter, TokenBucketLimiter])
async def test_fails_open_when_redis_is_down(cls) -> None:
    limiter = cls(BrokenRedis(), "x", 5, 60, 90)  # type: ignore[arg-type]
    result = await limiter.check("a")
    assert result.allowed and result.remaining == 5
