from collections.abc import Awaitable, Callable
from functools import lru_cache

from culinary_blog.auth.wiring import get_authenticator
from culinary_blog.cache.redis import get_ratelimit_redis
from culinary_blog.config import get_settings
from culinary_blog.ratelimit.dependencies import ClientIpResolver, IdentifierHasher, RateLimitGuard
from culinary_blog.ratelimit.limiter import SlidingWindowLimiter, TokenBucketLimiter


@lru_cache
def _guard() -> RateLimitGuard:
    settings = get_settings()
    hasher = IdentifierHasher(settings.ratelimit_hash_key.encode())
    return RateLimitGuard(ClientIpResolver(settings.trusted_proxy_list), hasher)


def auth_rate_limit() -> Callable[..., Awaitable[None]]:
    """`/api/v1/auth/*`: sliding window per IP (10/min)."""
    s = get_settings()
    limiter = SlidingWindowLimiter(
        get_ratelimit_redis(),
        "auth",
        s.auth_rate_limit_per_minute,
        s.rate_limit_window_seconds,
        s.rate_limit_key_ttl_seconds,
    )
    return _guard().per_ip(limiter)


def api_rate_limit() -> Callable[..., Awaitable[None]]:
    """General API reads (ADR-0006): token bucket per IP (100/min, bursts allowed); writes are not drawn from it."""
    s = get_settings()
    limiter = TokenBucketLimiter(
        get_ratelimit_redis(),
        "api",
        s.api_rate_limit_per_minute,
        s.rate_limit_window_seconds,
        s.rate_limit_key_ttl_seconds,
    )
    return _guard().per_ip(limiter, methods=frozenset({"GET", "HEAD"}))


def upload_rate_limit() -> Callable[..., Awaitable[None]]:
    """Image upload: sliding window, 5/min, enforced per IP and per user."""
    s = get_settings()
    limiter = SlidingWindowLimiter(
        get_ratelimit_redis(),
        "upload",
        s.upload_rate_limit_per_minute,
        s.rate_limit_window_seconds,
        s.rate_limit_key_ttl_seconds,
    )
    return _guard().per_ip_and_user(limiter, get_authenticator())
