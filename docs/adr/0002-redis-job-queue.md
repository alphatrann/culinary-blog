# ADR-0002: Redis (not Postgres, not RabbitMQ) for the job queue

## Status

Accepted

## Context

- Three background job types need a queue: welcome email (FR-JOB-001), thumbnail generation (FR-JOB-002), sitemap generation (FR-JOB-003).
- Alternatives considered: Postgres-as-queue (`jobs` table, `LISTEN/NOTIFY`), RabbitMQ.
- All three job types tolerate loss: a lost welcome email isn't resent, a failed thumbnail falls back to the original image, a failed sitemap run retries on the next day's cron.

## Decision

Dedicated Redis instance (separate from the cache Redis instance — see ADR-0004 for its config) as the job queue: one queue + one DLQ per job type, consumed by standalone worker containers.

## Consequences

- Redis list ops (`LPUSH`/`BRPOP`) are O(1) and don't compete with read/write traffic for the primary database's connection pool — the standard reason Redis-backed queues (RQ, Celery, BullMQ) exist.
- Postgres-as-queue was right to reject: polling competes with OLTP traffic, and `LISTEN/NOTIFY` doesn't durably queue across a subscriber restart.
- RabbitMQ's routing/priority features and stronger delivery guarantees aren't needed given the job-loss tolerance above.
- **Scope boundary:** this reasoning applies only to these three job types. A future job with a correctness requirement (anything touching money, or anything where a dropped job produces user-visible inconsistent state) should revisit Redis's durability profile (ADR-0004) or reconsider RabbitMQ/a transactional outbox — not reuse this ADR's justification by default.
