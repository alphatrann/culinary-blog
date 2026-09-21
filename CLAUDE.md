# CLAUDE.md

Conventions for agents working in this repo. Source of truth is `docs/srs.md` (Vietnamese); ADRs in `docs/adr/` record why. If code and SRS disagree, update the SRS (and add an ADR for architectural decisions) rather than silently diverging.

## Commands

```
uv sync
uv run ruff check . && uv run ruff format .   # lint + format (line length 120)
uv run lint-imports                           # architecture contracts (must pass)
uv run pytest
uv run alembic revision --autogenerate -m "msg" && uv run alembic upgrade head
uv run culinary-blog                          # run API (deps via compose.development.yml)
uv run culinary-blog-image-worker             # thumbnails + file cleanup jobs (run alongside the API)
```

## Architecture: lightweight CQRS (CONS-001, NFR-MAINT-004, ADR-0001)

Direction is one-way: `router → command/query handlers → repository → models/schemas`.

```
src/culinary_blog/
  cqrs.py              # Command, Query, CommandHandler, QueryHandler bases
  <module>/
    router.py          # HTTP only
    commands/          # one handler class per write use case
    queries/           # one handler class per read use case
    repository.py      # the ONLY place that runs SQLModel queries
    models.py          # SQLModel entities, no FastAPI/HTTP imports
    schemas.py         # Pydantic request/response models
    wiring.py          # composition root: builds concrete deps, returns the APIRouter
```

- Reference implementation: `src/culinary_blog/health/`. Copy its shape for new modules.
- **OOP, not top-level functions**: routers, handlers and repositories are classes; dependencies come in through `__init__`. Routers are classes that own an `APIRouter` and register bound methods.
- One handler class per use case in its own file. A command/query is a `@dataclass(frozen=True)` subclass of `Command`/`Query`; handlers expose `async handle(...)`.
- Command handlers: authorization, business rules, multi-repository transactions, cache invalidation, enqueue jobs. Query handlers: reads and cache-aside only; never write.
- Command and query handlers must not import each other. Handlers, repositories and models must not import `fastapi`/`starlette`. Routers don't touch repositories.
- When adding a module, add it to `containers` in the `[tool.importlinter]` layers contract in `pyproject.toml`.
- No mediator/bus. The router builds the command/query and calls the handler directly.

## Code conventions

- Python 3.12, FastAPI, fully `async`. Type-annotate everything (NFR-MAINT-001: ruff + type checker clean).
- Validation lives in Pydantic schemas at the router boundary; no manual validation in handlers (CONS-002).
- JSON fields are `snake_case` (CONS-005). REST, versioned under `/api/v1/`. Errors are RFC 7807 `application/problem+json`. (Health endpoints are unversioned infra endpoints.)
- Entities extend `BaseModel` (`id`, `created_at`, `updated_at`, `is_deleted`, `row_version`). Soft delete only; repositories filter `is_deleted == false` by default. Use `row_version` for optimistic concurrency.
- PostgreSQL only; schema changes via Alembic autogenerate from SQLModel (CONS-006). Never build SQL from unparameterized user input.
- Auth: stateless JWT in HttpOnly cookies (`SameSite=Lax`, `Secure`), access 15 min, refresh 7 days (512-bit random, store SHA-256 hash). Passwords: Argon2id or bcrypt via `passlib` (CONS-004). Authorization is checked in handlers, not only routers; log every write with `user_id` + timestamp.
- Three separate Redis instances: cache, job queue, rate limit. Never mix responsibilities (ADR-0002..0007). Background work goes through the job queue and standalone workers, not in-process background tasks (CONS-008).
- Uploads: max 5 MB; jpeg/png/webp/avif; verify magic bytes, not just Content-Type (CONS-007). Storage goes through the `FileStorageService` abstraction; file names `{folder}/{uuid4()}{ext}`.
- Logging: structured JSON, every entry carries `correlation_id`, `request_path`, and `user_id` when authenticated (CONS-010).
- Config comes from env via `culinary_blog/config.py`; the app must import with no live services (see `tests/test_smoke.py`).

## Testing (NFR-MAINT-002)

- Unit tests for handlers with a faked repository, ≥80% line coverage on the handler layer.
- Every endpoint: at least one happy-path and one error-case integration test.
- Test files mirror source in `tests/`; see `tests/test_health.py`.

## Process

- ADR for every significant architectural decision (`docs/adr/NNNN-title.md`); keep CHANGELOG.md per release (Keep a Changelog + SemVer).
- Conventional commits (`feat(api): ...`, `chore(ci): ...`, `docs: ...`); branch off `main`, PR into `main`, at least one reviewer.
- Don't edit `migrations/versions/` by hand except to fix autogenerate output.
