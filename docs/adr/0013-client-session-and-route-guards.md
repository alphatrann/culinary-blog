# ADR-0013: Client-side session and route guards

## Status

Accepted

## Context

- Header, forms and the author area need the current user; `/dashboard/**` and `/profile` must not render for guests; `/auth/*` should bounce signed-in users (SRS route table).
- Public pages are SSR/ISR and must stay anonymous and cacheable (ADR-0012: server components send no cookies).
- The access cookie lives 15 minutes and the refresh cookie is scoped to `/api/v1/auth`, so Next middleware cannot distinguish "access expired but refreshable" from "guest".

## Decision

- `useUser()` (`web/src/lib/session.ts`) wraps `GET /auth/me` in TanStack Query under key `["auth","me"]`. A 401 (after the client's silent refresh) resolves to `null` = guest. `logout()` calls `POST /auth/logout`, then sets the cache to guest and navigates home. `api.onSignedOut` also sets the cache to guest.
- Guards are client components in route-group layouts: `RequireAuth` (`/dashboard`, `/profile`; optional any-of `roles`, admin satisfies all) redirects guests to `/auth/login?next=<path>` and shows a 403 state for missing roles; `GuestOnly` (`/auth/*`) redirects signed-in users to `?next=` or `/`. `?next=` is validated by `safeNext` (same-origin relative paths only).
- No Next middleware. The API remains the real authorization boundary (CONS-004); guards are UX only.

## Consequences

- Protected pages show a skeleton until `/auth/me` resolves; their markup is never user-specific on the server.
- Layouts are server components, so public routes keep their static/ISR output.
