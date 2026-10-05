# Roadmap

## Must-Have

### ✅ M0 — Infra skeleton
- Docker Compose: Postgres, 3× Redis, MinIO
- FastAPI scaffold, SQLModel entities, initial migration
- `/health`, `/health/live`, `/health/ready`

### ✅ M1 — Auth core (FR-AUTH-001/002/004/005)
- Register (Argon2id), login with HttpOnly cookies, lockout after 5 failures
- Refresh with rotation, logout with revocation
- RFC 7807 errors, `GET /auth/me`

### ✅ M2 — Categories (FR-CAT-001–004)
- Public list and detail (with published recipes)
- Admin create and update

### ✅ M3a — Recipe CRUD (FR-RCP-001–004)
- Create (draft, unique slug), update with `If-Match` / `row_version`
- List with filter, sort, pagination and role-based visibility
- Detail with eager-loaded relations

### ✅ M3b — Ingredients & steps (FR-RCP-009/010)
- Add / update / delete both
- Steps auto-numbered and renumbered on delete

### ✅ M3c — Publishing (FR-RCP-005)
- `PATCH /recipes/{id}/publish` and `/unpublish`
- Requires ≥1 step and ≥1 ingredient (else 422)

### ✅ M4 — Images (FR-RCP-008, FR-FILE-001/002)
- Upload to MinIO (MIME + magic bytes, ≤5 MB)
- First image is primary; set-primary endpoint
- Delete, auto-promoting another image
- `resize_image` job + minimal worker for thumbnails (`uv run culinary-blog-image-worker`)

### ✅ M5a — Soft delete (FR-RCP-007)
- `DELETE /recipes/{id}` cascades to steps, ingredients, images

### ✅ M5b — Full-text search (FR-SRCH-001)
- `unaccent` + `pg_trgm`, GIN trigram index on `f_unaccent(lower(title))` (ADR-0008)
- `GET /recipes/search`, published only, ranked by `word_similarity` (`relevance_score`)

### ✅ M6a — Load-test baseline (NFR-PERF-001/002/004)
- k6 smoke, load (100 users) and stress scripts, 10k-recipe seed, `EXPLAIN ANALYZE` script (`loadtest/`)
- Baseline passes NFR-PERF-001/002 uncached (p95 ≤ 30 ms reads at 100 users); knee at ~100–150 stress VUs (API CPU-bound)
- Decision: no new indexes at SRS scale; DB round-trip fixes, nginx/OTel fixes (see `loadtest/README.md`)

### ✅ M6b — Cache layer (NFR-PERF-001/003, ADR-0003, ADR-0005, ADR-0010)
- Cache-aside: categories 1h, recipes 30m, search 5m; guest-only for lists/category pages; detail uses SWR + mutex
- Invalidation on create / update / publish / unpublish / delete / children / image variants; generation counter for query keys
- Cache Redis down → Postgres fallback
- Load test re-run (TTLs lowered): 83.6% served from cache, p95 21 → 13 ms overall; stress p95 passes at 150 VUs (195 ms, was 537 ms), still misses at 200 (`loadtest/README.md`)

### M7 — Frontend MVP (#22)
Next.js app in `web/`, built from the design mockups in `mockups/`. Deferred to Should-Have: Google button (S1), profile info editing (S2), archived tab (S3). Search has no sort dropdown (API is relevance-only); "featured" on home is the newest recipe.

#### M7a — Foundation
- [ ] #31 Scaffold `web/` (Next.js App Router, TS, Tailwind, Docker, nginx)
- [ ] #32 Design tokens, fonts and UI primitives
- [ ] #33 API client, RFC 7807 errors and silent refresh

#### M7b — Shared layout
- [ ] #34 Header and Footer
- [ ] #35 RecipeCard, grid, pagination and filter bar

#### M7c — Public pages
- [ ] #36 Home (`/`)
- [ ] #37 Recipe list (`/recipes`)
- [ ] #38 Recipe detail (`/recipes/[slug]`)
- [ ] #39 Categories (`/categories`, `/categories/[slug]`)
- [ ] #40 Search (`/search`)

#### M7d — Auth
- [ ] #41 Session layer and route guards
- [ ] #42 Login and register pages

#### M7e — Author area
- [ ] #43 [backend] Filter recipe list by author and status
- [ ] #44 Recipe editor: create
- [ ] #45 Image upload panel
- [ ] #46 Recipe editor: edit
- [ ] #47 Author dashboard and my recipes

#### M7f — Quality & delivery
- [ ] #48 Responsive and accessibility pass, e2e smoke tests
- [ ] #49 Web CI, Lighthouse budgets and ADR-0011

## Should-Have

### S1 — Google OAuth (FR-AUTH-003)
- [ ] Verify ID token, create/link user
- [ ] "Sign in with Google" button

### S2 — Profile (FR-AUTH-006/007)
- [ ] View and edit name, avatar, bio

### S3 — Archive & category guard (FR-RCP-006, FR-CAT-005)
- [ ] Archive / unarchive recipes
- [ ] Block deleting non-empty categories (409)

### S4 — Workers, logging & SEO (FR-JOB-001–003, FR-OBS-001, NFR-SEO-001–004)
- [ ] Welcome-email worker (3 retries → DLQ)
- [ ] Harden resize worker (3 retries → DLQ)
- [ ] Sitemap worker + daily 02:00 UTC cron
- [ ] JSON logs with `correlation_id`, OTel → Grafana
- [ ] JSON-LD, Open Graph, Twitter Cards, canonical URLs
