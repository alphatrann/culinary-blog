# ADR-0004: Job Queue Redis persistence, eviction, and queue topology

## Status

Accepted

## Context

- Job queue Redis instance (separate from cache Redis — ADR-0002/ADR-0003) needs a durability profile that behaves very differently from cache data: losing a cached value is a cheap, self-healing miss; losing a queued job is silent, permanent data loss.

## Decision

- `appendonly yes`, `appendfsync everysec`.
- `maxmemory-policy noeviction`.
- Topology: `{queue_name}` + `{queue_name}:dlq` per job type — 3 job types × 2 = 6 structures (welcome email, image resize, sitemap).

## Consequences

- `noeviction` is the only defensible policy here — copying cache Redis's `allkeys-lfu` (ADR-0003) would be an actual bug: evicting a queued job under memory pressure isn't a cache miss, it's a job that silently never runs.
- `appendfsync everysec` bounds crash data loss to ~1s of writes — the standard middle ground between `always` (throughput cost) and `no` (reopens the exact problem this instance exists to avoid).
- Per-job-type queues + DLQs mean a failure spike in one job type (e.g. MinIO downtime hitting `resize_image:dlq`) is immediately distinguishable from an unrelated failure elsewhere, without inspecting payloads.
- **Follow-up:** `noeviction` protects correctness but not availability — if workers fall behind or go down, this instance can hit OOM and start rejecting *new* enqueues (e.g. image uploads stop scheduling a resize). Put a memory-usage alert on this instance specifically; this isn't a reason to change the eviction policy.
