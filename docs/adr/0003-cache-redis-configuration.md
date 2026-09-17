# ADR-0003: Cache Redis TTL tiers and eviction policy

## Status

Accepted

## Context

- Cache Redis instance (separate from the job queue instance — ADR-0002/ADR-0004) backs three tiers: category listings, recipe list/detail, search results.
- Categories change rarely; recipes more often (stale reads after an edit are more visible); search queries are numerous and one-off.

## Decision

- TTL: category list = 1h, recipe (list & detail) = 30min, search results = 5min.
- Eviction: `allkeys-lfu`, `maxmemory 2gb`, no persistence (cache is fully rebuildable from Postgres).

## Consequences

- TTL ordering tracks each tier's write frequency and staleness blast radius, not just query cost — the right axis to sort by.
- LFU over LRU assumes recipe popularity is roughly stable rather than trend-driven, which is reasonable for a recipe blog (popularity moves over weeks/months, not hours) — worth naming explicitly rather than defaulting to LRU.
- "2GB is headroom, not a constraint" holds only because every tier's TTL is already short; if any tier's TTL is pushed much longer later, re-check this assumption.
- **Revisit trigger:** if traffic ever becomes bursty/trend-driven (a recipe goes viral for a few hours), LFU actively fights the spike — it'll keep favoring steady performers over the newly-hot key. Switch to `allkeys-lru` or a hybrid if that happens; not worth solving preemptively.
