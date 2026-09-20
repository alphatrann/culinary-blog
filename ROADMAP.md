# Roadmap

## Must-Have

### M0 — Infra skeleton

**Covers:** foundational scaffolding, FR-OBS-001 (health checks — skeleton only; structured logging/tracing polish is S4)

- [x] Docker Compose (`compose.development.yml`) brings up Postgres, Cache Redis (ADR-0003), Job Queue Redis (ADR-0002/0004), Rate Limit Redis (ADR-0006/0007) — three separate Redis instances, each with its own eviction/persistence policy — and MinIO; the API runs natively via `uv run` for real hot reload; nginx, the containerized API image, and the one-shot `migrate` service are production-only (`compose.production.yml`); OTel Collector → Tempo/Loki/Prometheus → Grafana is also production-only, development relies on console/stdout logs
- [x] FastAPI project layout scaffolded
- [x] SQLModel models for all core entities (User, RefreshToken, Category, Recipe, RecipeStep, RecipeIngredient, RecipeImage) + Alembic initial migration
- [x] Bare `GET /health`, `GET /health/live`, `GET /health/ready` (dependency checks wired, no alerting/tracing yet)

**Demo:** `docker compose -f compose.development.yml up -d` (infra) → `uv run alembic upgrade head` → `uv run culinary-blog`, then `GET /health` → 200 with all deps healthy. The full containerized path (nginx + API image + `migrate`) is validated via `compose.production.yml`.

### M1 — Auth core

**Covers:** FR-AUTH-001, FR-AUTH-002, FR-AUTH-004, FR-AUTH-005

- [ ] FR-AUTH-001 registration (email/password, hashed storage)
- [ ] FR-AUTH-002 login issues access + refresh tokens as HttpOnly cookies
- [ ] FR-AUTH-004 refresh: 512-bit refresh tokens, rotated on every use
- [ ] FR-AUTH-005 logout revokes the current refresh token; a revoked/rotated-out token is rejected on reuse

**Demo:** via `/docs` — register → cookies set, call a protected endpoint, refresh, logout, confirm the revoked refresh token is now rejected.

### M2 — Categories

**Covers:** FR-CAT-001, FR-CAT-002, FR-CAT-003, FR-CAT-004

- [ ] FR-CAT-003 Admin create category
- [ ] FR-CAT-004 Admin update category
- [ ] FR-CAT-001 public list categories
- [ ] FR-CAT-002 public category detail + its published recipes
- [ ] No caching yet — direct DB reads (Cache Redis layer added in M6b)

**Demo:** Admin creates categories, `GET /categories` lists them, `GET /categories/{slug}` resolves.

### M3a — Recipe CRUD skeleton

**Covers:** FR-RCP-001, FR-RCP-002, FR-RCP-003, FR-RCP-004

- [ ] FR-RCP-003 create recipe (starts as `draft`, slug auto-generated + unique)
- [ ] FR-RCP-004 update recipe with optimistic concurrency (`row_version` / `If-Match` → 409 on mismatch)
- [ ] FR-RCP-001 paginated/filtered/sorted list with role-based visibility (Guest: published only; Author: published + own draft/archived; Admin: all)
- [ ] FR-RCP-002 recipe detail with eager-loaded steps/ingredients/images/category/author; draft/archived gated to owner or Admin (403 otherwise)
- [ ] No caching yet — direct DB reads (Cache Redis layer added in M6b)

**Demo:** Author creates a draft recipe and edits it (a stale `row_version` correctly 409s); Guest sees only published recipes in the list while the Author also sees their own draft; an unknown slug 404s.

### M3b — Ingredients & steps CRUD

**Covers:** FR-RCP-009, FR-RCP-010

- [ ] FR-RCP-009 ingredient add/update/delete; `quantity`/`unit` co-nullable rule enforced (both null or both set, `quantity > 0`)
- [ ] FR-RCP-010 step add/update/delete; `title` + `description` required, `step_number` always server-assigned
- [ ] Deleting a step renumbers the remaining steps to stay contiguous (1, 2, 3…)

**Demo:** Add two ingredients and two steps to a draft recipe (steps auto-numbered), delete step 1 and confirm step 2 renumbers to 1; posting an ingredient with `quantity` but no `unit` returns 422.

### M3c — Publish rule validation

**Covers:** FR-RCP-005

- [ ] `PATCH /recipes/{id}/publish` and `/unpublish` endpoints
- [ ] Publish blocked with 422 unless the recipe has ≥1 step **and** ≥1 ingredient
- [ ] `published_at` set on first publish; publish/unpublish is idempotent if already in the target state

**Demo:** Publishing a recipe with no steps/ingredients yet returns 422; after adding at least one of each (via M3b), publish succeeds and the recipe becomes visible to Guest in the public list/detail.

### M4 — Recipe images

**Covers:** FR-RCP-008, FR-FILE-001, FR-FILE-002

- [ ] FR-FILE-001 upload to MinIO (MIME allow-list, magic-byte check, ≤5MB, unique `{folder}/{uuid}.{ext}` path)
- [ ] First uploaded image auto-set as `is_primary`
- [ ] Set-primary endpoint (flips `is_primary` across the recipe's images)
- [ ] FR-FILE-002 delete endpoint; if the deleted image was primary and others remain, one is auto-promoted
- [ ] Enqueue a `resize_image` job onto Job Queue Redis after upload
- [ ] Minimal `image-resize-worker` consuming that queue to populate `thumbnail_url`/`medium_url` (full retry/DLQ hardening happens in S4)

**Demo:** upload an image via multipart form, see it as primary in the recipe detail response; thumbnail/medium URLs populate once the worker finishes; delete it, see it gone.

### M5a — Recipe soft delete

**Covers:** FR-RCP-007

- [ ] `DELETE /recipes/{id}` sets `is_deleted = true` on the recipe
- [ ] Cascades `is_deleted = true` to its steps, ingredients, and images
- [ ] Deleted recipes excluded from every normal query/listing, but still present and recoverable in Postgres

**Demo:** delete a recipe and confirm it's hidden (Guest and Author listings, detail returns 404) while `is_deleted = true` and all child rows are also marked deleted in the DB.

### M5b — Vietnamese full-text search

**Covers:** FR-SRCH-001

- [ ] `unaccent` + `pg_trgm` Postgres extensions installed
- [ ] Generated `search_vector` tsvector column, trigger-maintained on `title`/`description` change
- [ ] GIN index on `search_vector` (functionally required for search to work at all — not a cache)
- [ ] `GET /recipes/search` — `tsquery` + `ts_rank` ordering, published-only, same filter/sort/pagination shape as FR-RCP-001
- [ ] No Cache Redis caching yet — raw DB query path only (caching added in M6b)

**Demo:** searching "pho" matches "phở" via a direct (uncached) DB query; an empty or 1-character query returns 422.

### M6a — Load-test baseline (uncached)

**Covers:** NFR-PERF-001, NFR-PERF-002, NFR-PERF-004 (measurement phase, run against the M0–M5b API with no Cache Redis reads)

- [ ] k6 smoke test script
- [ ] k6 load test script (≥100 concurrent users, per NFR-PERF-002)
- [ ] k6 stress test script to find the breaking point
- [ ] Run all three against recipe list/detail, category, and search endpoints with Cache Redis not yet in the read path
- [ ] Capture actual p50/p95/p99 and compare against NFR-PERF-001 targets (p50≤150ms, p95≤500ms, p99≤1000ms)
- [ ] Enable Postgres slow query log (>100ms per NFR-PERF-004)
- [ ] Run `EXPLAIN ANALYZE` on the slow queries surfaced; document missing indexes and any N+1s found

**Demo:** a k6 report showing baseline p50/p95/p99 against the uncached API, plus a written list of concrete bottlenecks (slow queries / missing indexes / N+1s) found via `EXPLAIN ANALYZE` and the slow query log — this list is the input to M6b.

### M6b — Cache Redis layer + re-verification

**Covers:** NFR-PERF-001, NFR-PERF-003 (ADR-0003)

- [ ] Cache-aside reads wired: category list/detail (TTL 1h), recipe list/detail (TTL 30min), search results (TTL 5min)
- [ ] Event-driven invalidation: relevant keys cleared on category/recipe create, update, publish, delete
- [ ] Eviction config applied: `allkeys-lfu`, `maxmemory 2gb`, no persistence (ADR-0003)
- [ ] Any additional indexes / query fixes identified in M6a implemented
- [ ] Re-run the M6a k6 load test against the now-cached API

**Demo:** the repeated k6 load test now meets NFR-PERF-001 (p50≤150/p95≤500/p99≤1000ms) with Cache Redis hit rate ≥80% (NFR-PERF-003); editing a published recipe immediately invalidates its cached list/detail entry (no stale read on the next request).

### M7 — Frontend MVP

**Covers:** Next.js UI over M1–M6b

- [ ] Public pages: recipe list, recipe detail, category pages, search results
- [ ] Auth pages: login, register — cookie-based auth means no manual token storage/attachment on the frontend
- [ ] Author dashboard: recipe CRUD forms (create/edit/publish, ingredients/steps editors, image upload)

**Demo:** click through the live site end-to-end: browse → search → log in → create & publish a recipe → see it rendered at `/recipes/[slug]`.

## Should-Have

### S1 — Google OAuth

**Covers:** FR-AUTH-003

- [ ] Backend verifies a Google ID token and creates/links the user
- [ ] Frontend "Sign in with Google" button (Google Identity Services, client-side ID-token flow)

**Demo:** "Sign in with Google" button on the frontend logs a new user in.

### S2 — Profile

**Covers:** FR-AUTH-006, FR-AUTH-007

- [ ] View profile endpoint + page
- [ ] Update display name / avatar / bio (endpoint + form)

**Demo:** `/profile` page, edit display name/avatar/bio, persists.

### S3 — Archive + category delete guard

**Covers:** FR-RCP-006, FR-CAT-005

- [ ] FR-RCP-006 archive/unarchive: recipe vanishes from public list, stays visible to its owner
- [ ] FR-CAT-005 category delete blocked with 409 (+ recipe count) if it still has any recipes (draft/archived included); succeeds once empty

**Demo:** archive a recipe from the dashboard (vanishes from public list, still visible to owner); deleting a non-empty category is blocked with a clear error, deleting an empty one succeeds.

### S4 — Worker jobs, CronJobs & SEO polish

**Covers:** FR-JOB-001, FR-JOB-002, FR-JOB-003, FR-OBS-001 (full logging/tracing), NFR-SEO-001–004

- [ ] `welcome-email-worker` (FR-JOB-001): enqueued after registration, retry 3x (1m/5m/30m backoff) → `welcome_email:dlq`
- [ ] `image-resize-worker` hardened with full retry (3x) + DLQ policy → `resize_image:dlq` (extends the minimal worker from M4)
- [ ] `sitemap-worker` + `cronjobs` container triggering FR-JOB-003 daily at 02:00 AM UTC, retry 2x → `sitemap:dlq`
- [ ] Structured JSON logging with `correlation_id`, OTel traces/metrics → Tempo/Loki/Prometheus, visible on Grafana dashboards
- [ ] NFR-SEO: Schema.org Recipe JSON-LD, Open Graph + Twitter Card tags, canonical URLs on recipe pages

**Demo:** register → welcome email appears in Mailhog; upload an image → thumbnail/medium variants appear shortly after; CronJobs triggers the Sitemap Generator on schedule and `/sitemap.xml` is populated; recipe page source shows Schema.org Recipe JSON-LD + Open Graph tags.
