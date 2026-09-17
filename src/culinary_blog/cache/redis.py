from functools import lru_cache

from redis.asyncio import Redis

from culinary_blog.config import get_settings


@lru_cache
def get_cache_redis() -> Redis:
    return Redis.from_url(get_settings().cache_redis_url)


@lru_cache
def get_queue_redis() -> Redis:
    return Redis.from_url(get_settings().queue_redis_url)


@lru_cache
def get_ratelimit_redis() -> Redis:
    return Redis.from_url(get_settings().ratelimit_redis_url)
