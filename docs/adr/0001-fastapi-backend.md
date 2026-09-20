# ADR-0001: Backend on Python/FastAPI instead of .NET 10

## Status

Accepted

## Context

- Original SRS baseline (v1.0.0) specified a .NET 10 Minimal API backend: Clean Architecture, MediatR/CQRS, EF Core, ASP.NET Core Identity.
- Switched to Python before implementation started, confirmed by `container-diagram.png` and `pyproject.toml`.
- Stated reasons: broader ecosystem, less verbose than the C# + MediatR/CQRS pipeline, mature Redis SDKs.

## Decision

Build the backend in Python 3.12 + FastAPI (async), SQLModel for the ORM, Alembic for migrations — replacing MediatR pipeline behaviors, EF Core, ASP.NET Core Identity, and Hangfire.

## Consequences

- FastAPI + Pydantic collapses validation, serialization, and OpenAPI generation into one declarative step.
- Native `async`/`await` end-to-end fits this system's I/O-bound profile (Postgres, two Redis instances, MinIO, outbound HTTP to Google).
- Broadest Python ecosystem (image processing, scripting, future ML-adjacent features) is the strongest real justification — "mature Redis SDKs" doesn't hold up (`StackExchange.Redis` is arguably more mature than `redis-py`).
- Lose .NET's compiler-enforced Clean Architecture boundaries — replaced by the CQRS layering convention (CONS-001), enforced by code review and `import-linter` (layers contract, command/query handler independence, no FastAPI below the router; run in CI).
- Cross-cutting concerns (logging, validation, cache invalidation) are no longer free via MediatR pipeline behaviors — must be applied per-router/dependency deliberately; worth a shared base router or lint rule to avoid missing one on a new endpoint.
