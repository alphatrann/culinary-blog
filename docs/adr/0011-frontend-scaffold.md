# ADR-0011: Frontend scaffold (Next.js, Tailwind, shadcn/ui, same-origin routing)

## Status

Accepted

## Context

- SRS §6 / CONS-003 fix the frontend stack (Next.js App Router, TypeScript, Tailwind). M7a (#31) creates `web/`.
- Auth cookies are HttpOnly + `SameSite=Lax` (CONS-004), so browser and API must share an origin (SRS §5.2).
- Like the API (ADR-0009), the frontend needs real hot reload in development.

## Decision

- `web/` lives in this repo: Next.js 15 App Router, TypeScript strict, Tailwind CSS v4, shadcn/ui for primitives (components are copied into `src/components/ui`, so we own them), npm with a committed lockfile.
- **Same-origin routing in nginx:** `/api/`, `/health`, `/docs`, `/openapi.json` → FastAPI; everything else → Next.js. The browser calls `/api/v1` (`NEXT_PUBLIC_API_BASE_URL`); server components call the API directly over the compose network (`API_BASE_URL`, read at request time).
- **Production:** `web` is a compose service built from a standalone-output multi-stage `web/Dockerfile`. **Development:** no compose service; run `npm run dev` in `web/` next to `uv run culinary-blog`.
- The app must build with no live API: no data fetching at build time.

## Consequences

- No CORS configuration is needed.
- The nginx location regex must be extended when a new unversioned API path is added.
- The build downloads Google Fonts, so the image build needs internet access.
