# ADR-0014: Rendering per route, same-origin auth, and Lighthouse budgets

## Status

Accepted

## Context

- ADR-0011 fixed the scaffold and same-origin routing. M7 has now built the pages, so the rendering choice per route can be recorded from the code rather than from intent.
- Public recipe pages are SEO-sensitive (PRODUCT.md: Open Graph, JSON-LD, ISR). Dashboard and profile pages show per-user data behind a login.
- Auth cookies are HttpOnly and `SameSite=Lax` (CONS-004), so the browser must call the API on the same origin (SRS §5.2).
- M7f (#49) needs measurable performance targets that CI can enforce.

## Decision

**Rendering per route** (checked against the route files and the production build output):

| Route | Rendering | Why |
| --- | --- | --- |
| `/` | Static with `revalidate = 3600` (ISR) | Cacheable home page; the newest recipe changes slowly. |
| `/recipes/[slug]` | ISR with `revalidate = 300` | SEO page, read-mostly; a 5-minute staleness window is accepted. |
| `/recipes`, `/search` | `force-dynamic` (server-rendered per request) | The output depends on the query string (filters, search). |
| `/dashboard/*`, `/profile`, `/auth/*` | Client-rendered after the session check | Per-user and behind login. The server renders the shell; data is fetched from the browser through `/api/v1`. |

Server components call the API directly over the compose network (`API_BASE_URL`). Browser calls go through nginx on the same origin (`/api/v1`).

**Auth:** HttpOnly cookies, sent with `credentials: 'include'`. A 401 triggers one single-flight refresh and a retry (`ApiClient`). Route guards (`RequireAuth`, ADR-0013) redirect guests and check roles in the browser, and the API enforces authorization again on every write.

**Performance budgets** (`web/lighthouserc.json`, run by the `lighthouse` CI job against the compose stack, mobile preset, 3 runs, median):

- Largest Contentful Paint ≤ 2500 ms.
- Cumulative Layout Shift ≤ 0.1.
- Total Blocking Time ≤ 200 ms, as the proxy for INP. Lab runs have no INP metric.
- Script transfer size ≤ 200 KiB (gzip, as Lighthouse measures it).

Code splitting follows the routes: the recipe editor and the drag-and-drop library are only imported by dashboard pages, so public pages do not download them.

## Consequences

- A recipe page can show data up to 5 minutes old after an edit. The API's own cache is invalidated on write (ADR-0010); the page cache is separate and time-based.
- Dashboard and profile pages need JavaScript to show anything. This is acceptable for authenticated screens and keeps the server simple.
- Lab metrics are simulated and vary between runs. The budgets are a regression gate, not a field measurement. Revisit them when real traffic data exists.
- Raising a budget is a deliberate change to `lighthouserc.json` and should come with a note in this ADR.
