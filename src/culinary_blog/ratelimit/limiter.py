"""Redis-backed rate limiters (NFR-SEC-003, ADR-0006). HTTP-free; fail-open on any Redis error (SRS availability)."""

import logging
from dataclasses import dataclass
from typing import Protocol

from redis.asyncio import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

_REDIS_ERRORS = (RedisError, OSError, TimeoutError)

# Sliding window counter: weighted sum of the previous and current fixed windows. Atomic; time comes from Redis so
# API replicas never disagree on the clock. KEYS[1] = key prefix; the window counter keys are derived from it in-script
# (single-instance Redis, ADR-0007).
# ARGV: limit, window seconds, key ttl seconds. Returns {allowed, remaining, retry_after, reset_in}.
_SLIDING_WINDOW = """
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local ttl = tonumber(ARGV[3])
local now = redis.call('TIME')
local index = math.floor(now[1] / window)
local elapsed = (now[1] % window) + now[2] / 1000000
local current_key = KEYS[1] .. ':' .. index
local current = tonumber(redis.call('GET', current_key) or '0')
local previous = tonumber(redis.call('GET', KEYS[1] .. ':' .. (index - 1)) or '0')
local used = previous * (window - elapsed) / window + current
local reset_in = math.ceil(window - elapsed)
if used + 1 > limit then
  return {0, 0, math.max(reset_in, 1), math.max(reset_in, 1)}
end
redis.call('INCR', current_key)
redis.call('EXPIRE', current_key, ttl)
return {1, math.max(math.floor(limit - used - 1), 0), 0, math.max(reset_in, 1)}
"""

# Token bucket: capacity = limit, continuous refill of limit/window tokens per second, so a client may burst up to
# `limit` then sustains limit/window. KEYS[1] = hash {tokens, ts}. ARGV: capacity, window seconds, key ttl seconds.
_TOKEN_BUCKET = """
local capacity = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local ttl = tonumber(ARGV[3])
local rate = capacity / window
local now = redis.call('TIME')
local now_s = now[1] + now[2] / 1000000
local state = redis.call('HMGET', KEYS[1], 'tokens', 'ts')
local tokens = tonumber(state[1])
local ts = tonumber(state[2])
if tokens == nil or ts == nil then
  tokens = capacity
  ts = now_s
end
tokens = math.min(capacity, tokens + math.max(now_s - ts, 0) * rate)
local allowed = 0
local retry_after = 0
if tokens >= 1 then
  tokens = tokens - 1
  allowed = 1
else
  retry_after = math.max(math.ceil((1 - tokens) / rate), 1)
end
redis.call('HSET', KEYS[1], 'tokens', tostring(tokens), 'ts', tostring(now_s))
redis.call('EXPIRE', KEYS[1], ttl)
local reset_in = math.max(math.ceil((capacity - tokens) / rate), 0)
return {allowed, math.floor(tokens), retry_after, reset_in}
"""


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    reset_in: int  # seconds until the limit fully recovers; the HTTP layer turns it into X-RateLimit-Reset
    retry_after: int  # seconds to wait before retrying; 0 when allowed


class Limiter(Protocol):
    async def check(self, identifier: str) -> RateLimitResult: ...


class _RedisLimiter:
    def __init__(self, redis: Redis, name: str, limit: int, window_seconds: int, key_ttl_seconds: int) -> None:
        self._redis = redis
        self._name = name
        self._limit = limit
        self._window = window_seconds
        self._ttl = key_ttl_seconds

    def _fail_open(self) -> RateLimitResult:
        return RateLimitResult(allowed=True, limit=self._limit, remaining=self._limit, reset_in=0, retry_after=0)

    def _result(self, raw: list[int]) -> RateLimitResult:
        allowed, remaining, retry_after, reset_in = (int(v) for v in raw)
        return RateLimitResult(bool(allowed), self._limit, remaining, reset_in, retry_after)

    async def _run(self, script: str, keys: list[str]) -> RateLimitResult:
        try:
            raw = await self._redis.eval(script, len(keys), *keys, self._limit, self._window, self._ttl)  # type: ignore[misc]
        except _REDIS_ERRORS:
            logger.warning("rate limiter unavailable, failing open", extra={"limiter": self._name}, exc_info=True)
            return self._fail_open()
        return self._result(raw)


class SlidingWindowLimiter(_RedisLimiter):
    async def check(self, identifier: str) -> RateLimitResult:
        return await self._run(_SLIDING_WINDOW, [f"ratelimit:{self._name}:{identifier}"])


class TokenBucketLimiter(_RedisLimiter):
    async def check(self, identifier: str) -> RateLimitResult:
        return await self._run(_TOKEN_BUCKET, [f"ratelimit:{self._name}:{identifier}"])
