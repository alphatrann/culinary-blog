from functools import lru_cache

from redis.asyncio import Redis

from culinary_blog.config import get_settings


@lru_cache
def get_cache_redis() -> Redis:
    settings = get_settings()
    timeout = settings.cache_socket_timeout_seconds
    return Redis.from_url(settings.cache_redis_url, socket_timeout=timeout, socket_connect_timeout=timeout)


@lru_cache
def get_queue_redis() -> Redis:
    return Redis.from_url(get_settings().queue_redis_url)


@lru_cache
def get_ratelimit_redis() -> Redis:
    return Redis.from_url(get_settings().ratelimit_redis_url)
