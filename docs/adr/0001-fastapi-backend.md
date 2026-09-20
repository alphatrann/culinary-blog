# ADR-0001: Backend on Python/FastAPI

## Status

Accepted (replaces the original .NET 10 plan)

## Context

- The original SRS specified .NET 10 Minimal API with Clean Architecture, MediatR, EF Core and Identity.
- Python offers a broader ecosystem (image processing, scripting) and less boilerplate.

## Decision

Python 3.12 + FastAPI (async), SQLModel, Alembic.

## Consequences

- Pydantic unifies validation, serialization and OpenAPI generation.
- Native `async` fits the I/O-bound workload.
- No compiler-enforced layering: CQRS conventions (CONS-001) are enforced by `import-linter` in CI.
- No MediatR pipeline behaviors: logging, validation and cache invalidation must be applied explicitly.
