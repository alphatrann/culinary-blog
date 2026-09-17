# Culinary Blog

A recipe-sharing web platform: authors publish recipes with images, ingredients, step-by-step instructions, and nutrition info; readers browse, filter, and full-text search them. Built as a full-stack, API-driven reference project.

> Full requirements: [`docs/srs.md`](docs/srs.md) (SRS, IEEE 830 / ISO/IEC/IEEE 29148). Architecture decisions: [`docs/adr/`](docs/adr/). Build plan: [`ROADMAP.md`](ROADMAP.md).

## Status

Early scaffold. Backend project structure and dependencies are set up (`pyproject.toml`, `src/culinary_blog/`); no endpoints, models, or Docker Compose stack exist yet. See [`ROADMAP.md`](ROADMAP.md) for the milestone plan, starting at **M0 — Infra skeleton**.

## Tech Stack

| Layer            | Technology                                          |
| ---------------- | --------------------------------------------------- |
| Backend          | Python 3.12, FastAPI (async)                        |
| ORM / Migrations | SQLModel + Alembic                                  |
| Frontend         | Next.js (App Router), TypeScript                    |
| Database         | PostgreSQL 16                                       |
| Object Storage   | MinIO (S3-compatible)                               |
| Cache            | Redis 7 — dedicated instance                        |
| Job Queue        | Redis 7 — dedicated instance, separate from cache   |
| Rate Limiting    | Redis 7 — dedicated instance, separate from cache and job queue |
| Reverse Proxy    | Nginx                                               |
| Observability    | OpenTelemetry → Tempo / Loki / Prometheus → Grafana |

## Architecture

API-driven: a Next.js frontend and a FastAPI backend are independent processes talking over HTTPS/JSON REST, sitting behind Nginx. There is no shared server-side rendering or view engine between them.

```
Browser → Nginx → Next.js (web)
                → FastAPI (api) → PostgreSQL
                                → Cache Redis
                                → Job Queue Redis → Workers (resize / welcome-email / sitemap) + CronJobs
                                → Rate Limit Redis
                                → MinIO
                                → Google OAuth2 / SMTP
Backend → OpenTelemetry Collector → Tempo / Loki / Prometheus → Grafana
```

See [`docs/container-diagram.png`](docs/container-diagram.png) for the full container diagram, and [`docs/adr/`](docs/adr/) for why the backend is FastAPI (not the originally-specified .NET) and why cache, job-queue, and rate-limit state each live in their own Redis instance with independent eviction/persistence policies.

Backend layering is strict: `routers → services → repositories → models`, one direction only. Routers handle HTTP only; services hold business logic and cache/queue orchestration; repositories are the only place that runs a query.

## Scope

**In scope (v1.0.0):** recipe CRUD with draft/published/archived lifecycle, categories, Vietnamese full-text search, image upload with async thumbnail generation, email/password + Google login, role-based (Guest/Author/Admin) and resource-based authorization, background jobs (welcome email, image resize, sitemap), health checks.

**Out of scope (v1.0.0):** comments, ratings, bookmarks/favorites, real-time notifications, native mobile apps, payments, direct messaging, GraphQL.

## User Roles

| Role   | Access                                                                                                                                                                        |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Guest  | Browse and search published recipes and categories. Read-only.                                                                                                                |
| Author | Everything a Guest can do, plus create/edit/delete their own recipes (soft delete), manage ingredients/steps/images, publish/archive. Assigned automatically on registration. |
| Admin  | Everything an Author can do on _any_ recipe (always treated as a valid owner), plus manage categories.                                                                        |

## Key Design Decisions

Full context and consequences are in [`docs/adr/`](docs/adr/); summary:

| ADR                                                       | Decision                                                                                                                        |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| [0001](docs/adr/0001-fastapi-backend.md)                  | Backend on Python/FastAPI instead of the originally-specified .NET stack.                                                       |
| [0002](docs/adr/0002-redis-job-queue.md)                  | Redis (not Postgres, not RabbitMQ) for the background job queue.                                                                |
| [0003](docs/adr/0003-cache-redis-configuration.md)        | Cache Redis: per-tier TTLs (category 1h / recipe 30min / search 5min), `allkeys-lfu`, 2GB.                                      |
| [0004](docs/adr/0004-job-queue-redis-configuration.md)    | Job queue Redis: AOF `everysec`, `noeviction`, 3 queues + 3 DLQs.                                                               |
| [0005](docs/adr/0005-recipe-detail-cache-invalidation.md) | Recipe detail cache: stale-while-revalidate (soft/hard TTL) for expiring keys, mutex for cold keys.                             |
| [0006](docs/adr/0006-rate-limiting-strategy.md)           | Rate limiting: sliding window counter for auth, token bucket for general reads, sliding window (per-IP + per-user) for uploads. |
| [0007](docs/adr/0007-rate-limit-redis-configuration.md)   | Rate limit state: dedicated Redis instance, `allkeys-lru`, 4GB, RDB snapshot every minute.                                      |

## API

RESTful JSON, versioned under `/api/v1`. Auth is cookie-based (`access_token` / `refresh_token` as `HttpOnly` cookies) — no `Authorization: Bearer` header. Errors follow RFC 7807 Problem Details. All fields are `snake_case`. Once the API is running, interactive docs are auto-generated at `/docs` (Swagger UI) and `/redoc`.

## Getting Started

Prerequisites: Python 3.12+, [`uv`](https://docs.astral.sh/uv/).

```bash
uv sync
```

The full local stack (Postgres, three Redis instances — cache, job queue, rate limit — MinIO, Nginx, the Grafana observability stack) is planned as a single `docker compose up` — tracked as milestone **M0** in [`ROADMAP.md`](ROADMAP.md) and not yet committed to the repo. Until then there's no runnable API or `.env.example` to point at.

## Project Structure

```
src/culinary_blog/   # FastAPI application (routers / services / repositories)
docs/
  container-diagram.png
  srs.md             # Software Requirements Specification
  adr/               # Architecture Decision Records
ROADMAP.md           # Milestone-by-milestone build plan
```

## Documentation

- [`docs/srs.md`](docs/srs.md) — full SRS: functional requirements, non-functional requirements, data model, REST API spec.
- [`docs/adr/`](docs/adr/) — architecture decisions and their tradeoffs.
- [`ROADMAP.md`](ROADMAP.md) — Must-Have / Should-Have milestones mapped to FR/NFR IDs.
