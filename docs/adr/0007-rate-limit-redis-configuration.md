# ADR-0007: Rate limit Redis instance — eviction, memory, and persistence

## Status

Accepted

## Context

- Rate limit counters (ADR-0006) need different memory/durability characteristics than content cache (ADR-0003: `allkeys-lfu`) or the job queue (ADR-0004: AOF + `noeviction`).
- A counter's value is recency-based, not frequency-based: under memory pressure, the counters worth keeping are the ones for clients active right now, not the ones historically hit most.
- Losing counters occasionally (e.g. on restart) fails open — a client simply gets a fresh window — which is acceptable here, unlike job queue loss.

## Decision

- Dedicated Redis instance for rate limiting, separate from Cache Redis and Job Queue Redis.
- Eviction: `allkeys-lru`, `maxmemory 4gb`.
- Persistence: RDB snapshot every minute (`save 60 1`).

## Consequences

- LRU (not LFU) is correct for the opposite reason ADR-0003 chose LFU: a key that hasn't been touched in the current window is exactly the one that should be evicted first — recency, not historical frequency, is what matters for a rate-limit key.
- 4GB is generous relative to per-key counter size — headroom for many concurrent IPs/user_ids, not a tight budget; revisit only if this instance is asked to hold more than rate-limit state.
- RDB every minute is a reasonable middle ground for state that's allowed to reset: negligible overhead, but avoids every client re-earning a fresh window on every restart, not just on rare hard crashes.
- **Accepted consequence:** an unclean restart between snapshots silently resets in-flight counters — a temporary, unannounced drop in rate-limit protection (an attacker timing an attack around a restart gets a fresh window). Worth alerting on restarts of this instance specifically, not worth solving with stronger persistence.
- This is a third Redis instance, beyond the two already justified by ADR-0002/ADR-0004 — confirm this is intentional versus reusing Cache Redis, since Cache Redis's `allkeys-lfu` (ADR-0003) is the wrong policy for counters if they ever ended up sharing an instance.
