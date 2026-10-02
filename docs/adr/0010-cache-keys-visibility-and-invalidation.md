# ADR-0010: Cache keys, visibility and invalidation

## Status

Accepted

## Context

- M6b adds cache-aside on the Cache Redis for categories, recipe list/detail and search (NFR-PERF-003; TTLs and eviction are ADR-0003, the detail stampede pattern is ADR-0005).
- Three things the earlier ADRs leave open: (1) which responses are safe to share between viewers, (2) how to invalidate *query-shaped* keys (`recipes:list:{query_hash}`, search, category pages) without scanning, (3) what happens when the Cache Redis is down.
- Draft/archived recipes are visible only to their owner and Admins, so list and category-page results differ per viewer.

## Decision

- **Visibility.** Cache only what is identical for everyone. Recipe lists and category pages are cached for guests only; signed-in viewers always read Postgres. Search is published-only, so it is cached for everyone. Recipe detail is cached once under `recipe:{slug}` whatever its status; the owner/Admin check runs in the handler on every request, on cached data too, so authorization never depends on cache contents.
- **Generation counter instead of `DEL recipes:list:*`.** Query-shaped keys are `{namespace}:v{generation}:{sha256(params)}`. One global key `cache:generation` (no TTL) holds the generation. Invalidation is an atomic `INCR`; old generations are never read again and age out via TTL/LFU. `SCAN`/`KEYS` are never used on the request path.
  - Reads use a single Lua script that reads (and lazily seeds) the generation and `GET`s the key built from it, so the version lookup costs no extra round trip. On a miss the result is written under the generation returned by that script, i.e. the one in force *before* the database read. If a write bumps the generation meanwhile, the stale result lands in a dead generation and is never served.
  - The generation is seeded from the Redis clock (microseconds), so if `allkeys-lfu` ever evicts it the replacement cannot collide with an earlier generation whose entries are still alive.
- **Direct deletes** for single keys: `recipe:{slug}` and `categories:all`.
- **Who invalidates what** (done by command handlers after the DB write, through `RecipeCacheInvalidator` / `CategoryCacheInvalidator`):

  | Write | `recipe:{slug}` | generation bump | `categories:all` |
  |---|---|---|---|
  | create recipe | – | yes | – |
  | update recipe | yes | yes | only if the category changed |
  | publish / unpublish / delete recipe | yes | yes | yes (published counts change) |
  | steps, ingredients, images; image-worker variants | yes | no | no |
  | create category | – | – | yes |
  | update category | – | yes | yes |

  Publishing an already-published recipe (an idempotent no-op) invalidates nothing. Archive (S3) must use `visibility_changed` when it lands.
- **Cache down → Postgres.** Every Redis error is caught inside `RedisCache` and treated as a miss; invalidation errors are logged and bounded by TTL. The cache client uses short socket timeouts (`CACHE_SOCKET_TIMEOUT_SECONDS`, default 250 ms) so an outage costs milliseconds, not a hung request. Unreadable payloads (written by an older schema during a rolling deploy) are treated as misses.
- **Hit-rate metric.** `RedisCache` increments the OpenTelemetry counter `cache_requests{tier,result}` (`hit | stale | miss | error`). Redis `keyspace_hits` is not used: lock, revalidation-flag and generation keys would pollute it.

## Consequences

- One invalidation call covers every list, search and category-page key at once; the cost is that any recipe write drops *all* cached lists, even for unrelated filters. Acceptable at this write rate (a handful of authors); revisit with per-category generations if writes become frequent.
- Signed-in list and category-page reads are uncached, so the hit rate in a mixed workload is bounded by the share of guest traffic. Guests are the bulk of a public recipe blog; a per-viewer key would add memory for almost no reuse.
- **Known staleness, accepted:** renaming a category leaves already-cached `recipe:{slug}` entries (which embed the category name) stale for up to their 30-minute TTL; the same will apply to author profile edits (S2). Both are rare and within ADR-0003's TTL trade-off.
- **Known race, accepted:** a detail read that loaded from Postgres just before a write commits can store the pre-write value after the invalidator's `DEL` ran. The window is one query long and the entry lives at most 30 minutes (and at most ~25 before it is revalidated). Lists don't have this race (see the generation note above).
- The stale-while-revalidate refresh runs as an in-process task. It is a cache refresh, not a job whose loss matters, so it is not a CONS-008 violation; a lost refresh just means the next stale read starts another.
- TTLs are overridable by environment (`CACHE_TTL_*_SECONDS`) solely so load tests can force expiry churn; production keeps the ADR-0003 values.
