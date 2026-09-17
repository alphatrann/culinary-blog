# ADR-0005: Stale-while-revalidate + mutex for recipe detail cache reads

## Status

Accepted

## Context

- Recipe detail (FR-RCP-002) is cached in Cache Redis, key `recipe:{slug}`, TTL 30min (ADR-0003).
- Two distinct cache-stampede scenarios can hit this key: (1) a hot key expires and many concurrent requests miss simultaneously; (2) the key doesn't exist yet (new recipe, cold start, evicted) and the first wave of requests races to populate it.
- Momentary staleness is acceptable for a recipe detail read — content doesn't need to be second-fresh.

## Decision

- **Key exists, near/past expiry (stampede-on-expire):** stale-while-revalidate. Store a soft-expiry timestamp alongside the cached value (Redis TTL alone only gives one expiry point). Inside the soft window: serve normally. Between soft and hard expiry: serve the stale value immediately and trigger exactly one background revalidation (guarded by a short-lived "revalidating" flag) rather than blocking the request. Past hard expiry (Redis key gone): falls through to the mutex path.
- **Key doesn't exist (stampede-on-miss):** mutex. First requester acquires a short-TTL Redis lock (`SET NX PX`), queries Postgres, and repopulates the cache. Other concurrent requesters poll briefly for the lock to release / key to appear, falling back to a direct DB read if the wait exceeds a bound.

## Consequences

- Covers both stampede modes with the right tool for each: SWR removes added DB load entirely on the common "hot key expiring" path; the mutex bounds DB load to exactly one concurrent query on the rarer "cold key" path.
- Needs the lock to carry its own TTL — without one, a crash mid-refresh deadlocks the key for every subsequent request.
- Scoped to single-key recipe-detail reads only. List/search caches (many distinct query-hash keys, ADR-0003) don't concentrate traffic on one key the same way — plain TTL expiry stays fine there; don't generalize this pattern to those tiers by default.
- Adds real complexity (extra Redis round trip for the lock/flag check, a background revalidation task) over plain cache-aside — justified here because a recipe-detail miss is a multi-table join (steps + ingredients + images + category + author), not a single-row lookup.
