# 🍜 Culinary Blog

Recipe-sharing platform. Authors publish recipes with images, ingredients, steps and nutrition info; readers browse, filter and search them (Vietnamese full-text).

**Status:** M0–M5a done (infra, auth, categories, recipes, ingredients/steps, publishing, images, soft delete). Next: full-text search (M5b).

## Stack

| Layer         | Tech                                  |
| ------------- | ------------------------------------- |
| Backend       | Python 3.12, FastAPI (async)          |
| Data          | PostgreSQL 16, SQLModel, Alembic      |
| Frontend      | Next.js (App Router), TypeScript      |
| Storage       | MinIO (S3-compatible)                 |
| Redis ×3      | Cache · Job queue · Rate limit        |
| Edge          | Nginx                                 |
| Observability | OpenTelemetry → Tempo/Loki/Prometheus → Grafana |

## Architecture

```
Browser → Nginx → Next.js
                → FastAPI → PostgreSQL
                          → Redis (cache / queue / rate limit)
                          → MinIO
                          → Workers + CronJobs
```

Backend is lightweight CQRS, one direction only, enforced by import-linter:

`router → command/query handlers → repository → models`

## Features

- Recipe CRUD with draft / published / archived lifecycle
- Categories, filtering, sorting, pagination
- Vietnamese full-text search
- Image upload with async thumbnails
- Email/password + Google login
- Guest / Author / Admin roles
- Background jobs: welcome email, image resize, sitemap

**Not in v1:** comments, ratings, favorites, notifications, mobile apps, payments, messaging, GraphQL.

## Quick Start

Requires Python 3.12+, [`uv`](https://docs.astral.sh/uv/), Docker Compose v2.

```bash
uv sync
docker compose -f compose.development.yml up -d   # Postgres, 3× Redis, MinIO
uv run alembic upgrade head
uv run culinary-blog
curl http://localhost:8000/health
```

API docs: `/docs` (Swagger) · `/redoc`

## API

- REST + JSON under `/api/v1`, `snake_case` fields
- Auth via `HttpOnly` cookies
- Errors as RFC 7807 problem details

## Layout

```
src/culinary_blog/
  cqrs.py       # base classes
  health/       # reference module
  auth/  categories/  recipes/
migrations/  docker/  config/  nginx/  observability/
docs/           # SRS + ADRs
```

## Docs

- [SRS](docs/srs.md): requirements, data model, API spec
- [ADRs](docs/adr/): architecture decisions
- [Roadmap](ROADMAP.md): milestones
