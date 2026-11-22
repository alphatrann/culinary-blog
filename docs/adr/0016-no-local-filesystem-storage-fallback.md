# ADR-0016: No local filesystem fallback for file storage

## Status

Accepted

## Context

- SRS (dependency table, "MinIO / S3") originally said to fall back to local filesystem storage in development when MinIO is unavailable.
- `FileStorageService` is abstract, but only `MinioFileStorage` was ever implemented. No fallback or config switch exists in code.
- `compose.development.yml` already runs MinIO for local development.
- API and workers (image resize, sitemap) run as separate processes/containers. A local-disk backend would need a volume shared between them, which the dev and prod compose files don't provide.

## Decision

- MinIO is required in every environment. There is no local filesystem backend.
- When MinIO is unavailable, uploads return HTTP 503 (`ServiceUnavailableError`), as in the SRS upload exception flow.
- The SRS is updated to match (dependency table and section 3.5).

## Consequences

- One storage backend to maintain and test; no environment-dependent behavior in the upload path.
- Developers without Docker cannot exercise uploads locally. Running `compose.development.yml` is the supported path.
- Reversing this needs a new ADR, a local `FileStorageService` implementation, and a shared volume for workers.
