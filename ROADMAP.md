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

### M5a — Soft delete (FR-RCP-007)
- [ ] `DELETE /recipes/{id}` cascades to steps, ingredients, images

### M5b — Full-text search (FR-SRCH-001)
- [ ] `unaccent` + `pg_trgm`, `search_vector` with GIN index
- [ ] `GET /recipes/search`, published only

### M6a — Load-test baseline (NFR-PERF-001/002/004)
- [ ] k6 smoke, load (≥100 users) and stress scripts
- [ ] Record p50/p95/p99 vs. targets (150 / 500 / 1000 ms)
- [ ] Slow query log, `EXPLAIN ANALYZE`, list bottlenecks

### M6b — Cache layer (NFR-PERF-001/003, ADR-0003)
- [ ] Cache-aside: categories 1h, recipes 30m, search 5m
- [ ] Invalidate on create / update / publish / delete
- [ ] Apply fixes from M6a, re-run load test (hit rate ≥80%)

### M7 — Frontend MVP
- [ ] Public: list, detail, categories, search
- [ ] Auth: login, register
- [ ] Author dashboard: recipe forms, editors, image upload

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
