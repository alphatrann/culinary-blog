"""Cache-aside over the Cache Redis (ADR-0003, ADR-0005, ADR-0010).

Every Redis failure degrades to "cache miss": the loader (Postgres) answers and the request never errors (NFR-REL-002).
"""

import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable

from opentelemetry import metrics
from pydantic import BaseModel
from redis.asyncio import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

GENERATION_KEY = "cache:generation"

_meter = metrics.get_meter(__name__)
_requests = _meter.create_counter(
    "cache_requests",
    description="Cache lookups by tier and outcome (hit | stale | miss | error); the NFR-PERF-003 hit-rate source.",
)

_REDIS_ERRORS = (RedisError, OSError, TimeoutError)

# One round trip: read (and lazily seed) the generation, then GET the key built from it. The generation is a
# microsecond timestamp when seeded, so if Redis evicts it the new value can never collide with an older generation.
_READ_VERSIONED = """
local generation = redis.call('GET', KEYS[1])
if not generation then
  local now = redis.call('TIME')
  generation = now[1] .. string.format('%06d', now[2])
  redis.call('SET', KEYS[1], generation, 'NX')
  generation = redis.call('GET', KEYS[1])
end
local value = redis.call('GET', ARGV[1] .. ':v' .. generation .. ':' .. ARGV[2])
return {generation, value}
"""

# Bump the generation (seeding it first so a missing key doesn't restart from 1).
_BUMP_GENERATION = """
if redis.call('EXISTS', KEYS[1]) == 0 then
  local now = redis.call('TIME')
  redis.call('SET', KEYS[1], now[1] .. string.format('%06d', now[2]))
end
return redis.call('INCR', KEYS[1])
"""

_RELEASE_LOCK = """
if redis.call('GET', KEYS[1]) == ARGV[1] then
  return redis.call('DEL', KEYS[1])
end
return 0
"""


class Cache(ABC):
    """Typed cache-aside. `loader` is the database read; it runs only on a miss (or when the cache is unavailable)."""

    @abstractmethod
    async def get_or_load[T: BaseModel](
        self, key: str, ttl_seconds: int, model: type[T], loader: Callable[[], Awaitable[T]]
    ) -> T:
        """Plain TTL cache-aside under one fixed key."""

    @abstractmethod
    async def get_or_load_versioned[T: BaseModel](
        self,
        namespace: str,
        query_hash: str,
        ttl_seconds: int,
        model: type[T],
        loader: Callable[[], Awaitable[T]],
    ) -> T:
        """Cache-aside for query-shaped keys, invalidated as a group by `bump_generation` (no key scanning)."""

    @abstractmethod
    async def get_or_load_swr[T: BaseModel](
        self, key: str, ttl_seconds: int, model: type[T], loader: Callable[[], Awaitable[T]]
    ) -> T:
        """Single-key read with stale-while-revalidate + mutex stampede protection (ADR-0005)."""

    @abstractmethod
    async def delete(self, *keys: str) -> None: ...

    @abstractmethod
    async def bump_generation(self) -> None:
        """Logically drop every versioned key (recipe lists, search results, category pages)."""


class RedisCache(Cache):
    def __init__(
        self,
        redis: Redis,
        *,
        soft_ttl_ratio: float = 0.8,
        revalidate_lock_ms: int = 10_000,
        load_lock_ms: int = 5_000,
        load_wait_seconds: float = 0.5,
        poll_interval_seconds: float = 0.025,
    ) -> None:
        self._redis = redis
        self._soft_ttl_ratio = soft_ttl_ratio
        self._revalidate_lock_ms = revalidate_lock_ms
        self._load_lock_ms = load_lock_ms
        self._load_wait_seconds = load_wait_seconds
        self._poll_interval_seconds = poll_interval_seconds
        self._read_versioned = redis.register_script(_READ_VERSIONED)
        self._bump_generation = redis.register_script(_BUMP_GENERATION)
        self._release_lock = redis.register_script(_RELEASE_LOCK)
        self._background: set[asyncio.Task[None]] = set()

    async def get_or_load[T: BaseModel](
        self, key: str, ttl_seconds: int, model: type[T], loader: Callable[[], Awaitable[T]]
    ) -> T:
        tier = _tier(key)
        try:
            raw = await self._redis.get(key)
        except _REDIS_ERRORS:
            return await self._unavailable(tier, loader)
        cached = _decode(model, raw)
        if cached is not None:
            _requests.add(1, {"tier": tier, "result": "hit"})
            return cached
        _requests.add(1, {"tier": tier, "result": "miss"})
        value = await loader()
        await self._store(key, value.model_dump_json(), ttl_seconds)
        return value

    async def get_or_load_versioned[T: BaseModel](
        self,
        namespace: str,
        query_hash: str,
        ttl_seconds: int,
        model: type[T],
        loader: Callable[[], Awaitable[T]],
    ) -> T:
        tier = _tier(namespace)
        try:
            generation, raw = await self._read_versioned(keys=[GENERATION_KEY], args=[namespace, query_hash])
        except _REDIS_ERRORS:
            return await self._unavailable(tier, loader)
        cached = _decode(model, raw)
        if cached is not None:
            _requests.add(1, {"tier": tier, "result": "hit"})
            return cached
        _requests.add(1, {"tier": tier, "result": "miss"})
        value = await loader()
        # Write under the generation read *before* the load: if it was bumped meanwhile, this stale result lands in a
        # dead generation and is never served.
        generation = generation.decode() if isinstance(generation, bytes) else generation
        await self._store(f"{namespace}:v{generation}:{query_hash}", value.model_dump_json(), ttl_seconds)
        return value

    async def get_or_load_swr[T: BaseModel](
        self, key: str, ttl_seconds: int, model: type[T], loader: Callable[[], Awaitable[T]]
    ) -> T:
        tier = _tier(key)
        try:
            raw = await self._redis.get(key)
        except _REDIS_ERRORS:
            return await self._unavailable(tier, loader)

        envelope = _decode_envelope(model, raw)
        if envelope is not None:
            soft_expires_at, value = envelope
            if time.time() < soft_expires_at:
                _requests.add(1, {"tier": tier, "result": "hit"})
                return value
            _requests.add(1, {"tier": tier, "result": "stale"})
            await self._revalidate_in_background(key, ttl_seconds, loader)
            return value

        _requests.add(1, {"tier": tier, "result": "miss"})
        return await self._load_under_lock(key, ttl_seconds, model, loader)

    async def delete(self, *keys: str) -> None:
        try:
            await self._redis.delete(*keys)
        except _REDIS_ERRORS:
            logger.warning("cache delete failed; entries expire by TTL", extra={"keys": list(keys)}, exc_info=True)

    async def bump_generation(self) -> None:
        try:
            await self._bump_generation(keys=[GENERATION_KEY])
        except _REDIS_ERRORS:
            logger.warning("cache generation bump failed; lists expire by TTL", exc_info=True)

    # --- stampede protection (ADR-0005) --------------------------------------------------------------------------

    async def _load_under_lock[T: BaseModel](
        self, key: str, ttl_seconds: int, model: type[T], loader: Callable[[], Awaitable[T]]
    ) -> T:
        """Stampede-on-miss: one caller loads and populates; the others wait briefly for the key to appear."""
        lock_key = f"lock:{key}"
        token = uuid.uuid4().hex
        try:
            acquired = bool(await self._redis.set(lock_key, token, nx=True, px=self._load_lock_ms))
        except _REDIS_ERRORS:
            return await loader()

        if acquired:
            try:
                value = await loader()
                await self._store(key, self._envelope(value, ttl_seconds), ttl_seconds)
                return value
            finally:
                await self._release(lock_key, token)

        deadline = time.monotonic() + self._load_wait_seconds
        while time.monotonic() < deadline:
            await asyncio.sleep(self._poll_interval_seconds)
            try:
                raw = await self._redis.get(key)
            except _REDIS_ERRORS:
                break
            envelope = _decode_envelope(model, raw)
            if envelope is not None:
                return envelope[1]
        return await loader()  # the holder is slow or died: read Postgres directly rather than block

    async def _revalidate_in_background[T: BaseModel](
        self, key: str, ttl_seconds: int, loader: Callable[[], Awaitable[T]]
    ) -> None:
        """Serve-stale path: exactly one caller (guarded by a short-lived flag) refreshes the entry."""
        try:
            first = await self._redis.set(f"revalidating:{key}", "1", nx=True, px=self._revalidate_lock_ms)
        except _REDIS_ERRORS:
            return
        if not first:
            return
        task = asyncio.create_task(self._refresh(key, ttl_seconds, loader))
        self._background.add(task)  # the loop only keeps weak references to tasks
        task.add_done_callback(self._background.discard)

    async def _refresh[T: BaseModel](self, key: str, ttl_seconds: int, loader: Callable[[], Awaitable[T]]) -> None:
        try:
            value = await loader()
        except Exception:
            # Includes "recipe no longer exists": the delete that removed it already dropped this key.
            logger.info("background revalidation skipped", extra={"key": key}, exc_info=True)
            return
        await self._store(key, self._envelope(value, ttl_seconds), ttl_seconds)

    def _envelope(self, value: BaseModel, ttl_seconds: int) -> str:
        soft_expires_at = time.time() + ttl_seconds * self._soft_ttl_ratio
        return f"{soft_expires_at:.3f}\n{value.model_dump_json()}"

    # --- helpers -------------------------------------------------------------------------------------------------

    async def _store(self, key: str, payload: str, ttl_seconds: int) -> None:
        try:
            await self._redis.set(key, payload, ex=ttl_seconds)
        except _REDIS_ERRORS:
            logger.warning("cache write failed", extra={"key": key}, exc_info=True)

    async def _release(self, lock_key: str, token: str) -> None:
        try:
            await self._release_lock(keys=[lock_key], args=[token])
        except _REDIS_ERRORS:
            pass  # the lock has its own TTL

    @staticmethod
    async def _unavailable[T: BaseModel](tier: str, loader: Callable[[], Awaitable[T]]) -> T:
        _requests.add(1, {"tier": tier, "result": "error"})
        logger.warning("cache unavailable, reading from the database", extra={"tier": tier}, exc_info=True)
        return await loader()


def _tier(key: str) -> str:
    return key.split(":", 1)[0]


def _decode[T: BaseModel](model: type[T], raw: bytes | str | None) -> T | None:
    """Parse a cached payload; anything unreadable (e.g. written by an older schema during a deploy) is a miss."""
    if raw is None:
        return None
    try:
        return model.model_validate_json(raw)
    except ValueError:
        return None


def _decode_envelope[T: BaseModel](model: type[T], raw: bytes | str | None) -> tuple[float, T] | None:
    if raw is None:
        return None
    text = raw.decode() if isinstance(raw, bytes) else raw
    soft, _, payload = text.partition("\n")
    try:
        value = _decode(model, payload)
        return (float(soft), value) if value is not None else None
    except ValueError:
        return None
