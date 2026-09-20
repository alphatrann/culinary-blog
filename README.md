# Culinary Blog

A recipe-sharing web platform: authors publish recipes with images, ingredients, step-by-step instructions, and nutrition info; readers browse, filter, and full-text search them. Built as a full-stack, API-driven reference project.

> Full requirements: [`docs/srs.md`](docs/srs.md) (SRS, IEEE 830 / ISO/IEC/IEEE 29148). Architecture decisions: [`docs/adr/`](docs/adr/). Build plan: [`ROADMAP.md`](ROADMAP.md).

## Status

**M0 — Infra skeleton**, **M1 — Auth core**, **M2 — Categories** and **M3a — Recipe CRUD skeleton** complete. M0: `docker compose -f compose.development.yml up` brings up Postgres, all three Redis instances, and MinIO; the API runs natively via `uv run` (hot reload, ADR-0009) and `GET /health` returns 200 with every dependency healthy. SQLModel entities and the initial Alembic migration exist for all core tables. M1 adds `/api/v1/auth/{register,login,refresh,logout,me}` (HttpOnly-cookie JWT auth, rotating refresh tokens). M2 adds `/api/v1/categories` (public list/detail, Admin create/update). M3a adds `/api/v1/recipes`: `POST` (create as draft), `GET` (paginated/filtered/sorted list with role-based visibility), `GET /{slug}` (full detail) and `PUT /{id}` (update guarded by `If-Match: <row_version>` optimistic concurrency, 409 on a stale version). Ingredient/step CRUD (M3b), publish rules (M3c), images, search and caching are not implemented yet. See [`ROADMAP.md`](ROADMAP.md) for the milestone plan.

## Tech Stack

| Layer            | Technology                                                      |
| ---------------- | --------------------------------------------------------------- |
| Backend          | Python 3.12, FastAPI (async)                                    |
| ORM / Migrations | SQLModel + Alembic                                              |
| Frontend         | Next.js (App Router), TypeScript                                |
| Database         | PostgreSQL 16                                                   |
| Object Storage   | MinIO (S3-compatible)                                           |
| Cache            | Redis 7 — dedicated instance                                    |
| Job Queue        | Redis 7 — dedicated instance, separate from cache               |
| Rate Limiting    | Redis 7 — dedicated instance, separate from cache and job queue |
| Reverse Proxy    | Nginx                                                           |
| Observability    | OpenTelemetry → Tempo / Loki / Prometheus → Grafana             |

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

Backend is lightweight CQRS, strictly one direction: `router → command/query handlers → repository → models`. Routers handle HTTP only; command handlers own writes, cache invalidation and job enqueueing; query handlers own reads and cache-aside; repositories are the only place that runs a query. Enforced by import-linter in CI.

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

Prerequisites: Python 3.12+, [`uv`](https://docs.astral.sh/uv/), Docker Desktop / Docker Engine + Compose v2.

```bash
uv sync

docker compose -f compose.development.yml up -d
```

Brings up Postgres, three Redis instances (cache, job queue, rate limit), and MinIO, each publishing its port to `localhost`. The API is **not** containerized in development — it runs natively for real hot reload (no bind-mount, no rebuild step; see [ADR-0009](docs/adr/0009-dev-api-runs-natively.md)):

```bash
uv run alembic upgrade head
uv run culinary-blog
```

Once running:

```bash
curl http://localhost:8000/health
```

returns `200` with every dependency reported healthy. Auth cookies are `Secure` by default, so for plain-http local runs (cURL, `/docs`) set `COOKIE_SECURE=false` in `.env.development`; outside development `JWT_SECRET_KEY` must be set; interactive docs are at `http://localhost:8000/docs`. nginx, the containerized API image, and the observability stack (OTel Collector → Tempo/Loki/Prometheus → Grafana) only run in `compose.production.yml`.

## Project Structure

```
src/culinary_blog/
  main.py             # FastAPI app instance, middleware, router registration
  config.py           # Settings (env vars)
  database/           # BaseModel mixin, async engine/session
  cache/              # Cache / Job Queue / Rate Limit Redis clients
  cqrs.py             # Command / Query / handler base classes
  health/             # router.py, queries/, repository.py, wiring.py — reference CQRS module
  auth/               # M1: router, commands/, queries/, repository, security (Argon2id + JWT), cookies, wiring
  errors.py, problem_details.py  # domain errors → RFC 7807 responses
  categories/                    # M2: router, commands/, queries/, repository, slug, wiring
  recipes/                       # M3a: router, commands/, queries/, repository, mapping, wiring (steps/ingredients/publish/images land in M3b–M4)
migrations/           # Alembic env + versions
docker/               # Per-service Dockerfiles (config baked in, not bind-mounted)
config/               # Redis conf files (per ADR-0003/0004/0007)
nginx/, observability/
compose.development.yml, compose.production.yml
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
