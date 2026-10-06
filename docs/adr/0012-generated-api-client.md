# ADR-0012: Generated API types and a single fetch client

## Status

Accepted

## Context

- Pages talk to `/api/v1` with HttpOnly cookies; SRS §5.2 forbids `Authorization` headers, errors are RFC 7807, and FR-AUTH-004 requires refresh on 401.
- Hand-written types drift from the backend.

## Decision

- `scripts/export_openapi.py` dumps the FastAPI schema to `web/openapi.json`; `openapi-typescript` generates `web/src/lib/api/schema.d.ts`. `npm run api:sync` runs both; CI re-runs it and fails on any diff.
- `web/src/lib/api/client.ts` is a small typed wrapper (no codegen runtime): `credentials: 'include'`, JSON or multipart, `If-Match` from `rowVersion`, `X-Correlation-ID` (generated or passed through).
- Non-2xx responses become `ApiError` (status, title, detail, `errors` map keyed by field path).
- A 401 triggers one `POST /auth/refresh` shared by all concurrent requests (single-flight, because refresh rotates the token and a second call would trip reuse detection), then the request is retried. If refresh fails, `onSignedOut` listeners fire and the 401 is thrown. Auth endpoints themselves are never refreshed.
- Server components use `serverGet` (`web/src/lib/api/server.ts`): no cookies, ISR-cacheable. Authenticated data is fetched in the browser.
- TanStack Query is the browser data layer; 4xx errors are not retried.

## Consequences

- A backend schema change requires committing the regenerated files.
- `If-Match` is added to the CORS allowed headers for completeness, although production is same-origin.
