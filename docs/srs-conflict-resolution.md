# SRS conflicts: original vs. current

Compares `docs/base_srs.md` (original, conflicting) with `docs/srs.md` (current).
Only requirement-level conflicts are listed; framework and technology swaps are ignored.

Legend: ✅ resolved · ⚠️ partly resolved (leftover inconsistency) · ❌ still open

## Scoreboard

| Status | Count |
| ------ | ----- |
| ✅ Resolved | 44 |
| ⚠️ Partly resolved | 1 (#27e, cosmetic: validation vs DB column lengths) |
| ❌ Still open | 0 |
| 🆕 New conflict (N1) | fixed |

---

## 1. Counts

| # | Conflict in original | Current SRS | Status |
| - | -------------------- | ----------- | ------ |
| 1 | §1.5/§2.2/Ch.3 say **27 FR**, but the table sums to 34 | Now **29**, and the table sums to 29 (SRCH 4→1, OBS 3→1; FR-SRCH-002/3/4 folded into FR-RCP-001/SRCH-001, logging and tracing demoted to "implementation notes") | ✅ |
| 2 | NFR-SEC count says **6**, 7 are listed | Count is **7** | ✅ |

## 2. Delete semantics

| # | Original | Current | Status |
| - | -------- | ------- | ------ |
| 3 | FR-RCP-007 **hard delete** vs NFR-REL-003 / Ch.7 / §8.3 **soft delete** | Soft delete everywhere: FR-RCP-007, NFR-REL-003, §8.3, glossary. MinIO files are no longer removed at recipe delete (only on explicit image removal or a cleanup job) | ✅ |
| 4 | FR-CAT-005 physical delete vs §8.2 soft delete | FR-CAT-005 now says "soft delete", `is_deleted = true` | ✅ |

## 3. Recipe lifecycle

| # | Original | Current | Status |
| - | -------- | ------- | ------ |
| 5 | Publish needs ≥1 step (FR-RCP-005, 422) vs ≥1 ingredient **and** step (App. B, 400) | Everywhere: ≥1 step **and** ≥1 ingredient, **422** (FR-RCP-005, §8.3, App. A, App. B) | ✅ |
| 6 | FR-RCP-006 titled "Archive / **Unarchive**" but no unarchive endpoint | FR-RCP-006 now defines `PATCH …/unarchive` (archived → draft). **But §8.3 still lists no `/unarchive` row.** | ✅ fixed (see round 2) |
| 7 | FR-RCP-002 viewing Draft/Archived: description "owner or Admin", precondition "Admin only", flow "owner or Admin" | All three say Admin **or owner** | ✅ |
| 8 | List visibility: description "Draft+Archived", flow "Draft only", FR-CAT-002 "Draft only", §8.3 "Published only" | FR-RCP-001 and FR-CAT-002 both say own draft **and** archived. **§8.3 `GET /recipes` still says "Published, paginated"** | ✅ fixed (see round 2) |
| 9 | Per-user results cached with query-string key only → possible draft leak | ADR-0010: only the Guest view is cached; logged-in users bypass the cache. Detail re-checks `status` on cached data | ✅ |

## 4. Cache TTLs

| # | Object | Original (conflicting values) | Current | Status |
| - | ------ | ----------------------------- | ------- | ------ |
| 10 | Category list | 60 min in-memory (FR) · 30 min Redis (NFR-PERF-003) · "no in-memory" (NFR-SCALE) | **1 h, Cache Redis** everywhere | ✅ |
| 11 | Recipe list | 15 min (FR) · 30 min (NFR) | **30 min** | ✅ |
| 11b | Recipe detail | 60 min (FR) · 5 min (NFR) · ISR 300 s | **30 min** in FR and NFR. §5.1 ISR `revalidate=300` is a separate (page) layer and is unchanged | ✅ |
| 12 | Search | "none or 5 min" (FR) · 1 min (NFR) | **5 min** in both | ✅ |

## 5. Auth

| # | Original | Current | Status |
| - | -------- | ------- | ------ |
| 13 | Refresh token 512-bit (FR) vs 128-bit (NFR-SEC-002) | 512-bit everywhere | ✅ |
| 14 | Reuse detection optional "paranoid mode" (FR-AUTH-004) vs mandatory (NFR-SEC-002) | FR-AUTH-004 A3 now **revokes all** the user's live tokens, matching NFR-SEC-002 | ✅ |
| 15 | Logout: requires valid access token vs A2 allows expired one | A2 now returns 401 if the access-token cookie is missing or expired | ✅ |
| 16 | "VerifiedAuthor" policy needs a confirmed email, but registration grants Author immediately and no confirmation flow exists | §2.3 still defines the policy; `users.email_confirmed` defaults to `false`; FR-RCP-003 still only requires Author/Admin; there is still no confirmation FR. The welcome-email "activation link" wording was removed | ✅ fixed (see round 2) |
| 17a | Lockout 423 reveals the account exists vs anti-enumeration (A1) | Unchanged. 423 is still returned with no mention in App. A or §8.1 | ✅ fixed (see round 2) |
| 17b | `AUTH_ACCOUNT_DISABLED` (403) in App. B, unhandled in FR-AUTH-002 | Unchanged. FR-AUTH-002 handles lock only. FR-AUTH-004 A4 returns 401 for "khóa" | ✅ fixed (see round 2) |
| 18 | Register request/response shape differs (FR returns tokens and `fullName`/`userName`; §8.1 returns `{userId…}` and `displayName`) | One shape: request `{display_name,email,password}`, response `{id,display_name,email,avatar_url,roles}` with tokens in cookies, in both FR and §8.1 | ✅ |
| 19 | Profile fields differ (FR: fullName/userName/emailConfirmed; §8.1: displayName/bio) | Both use `display_name`, `avatar_url`, `bio`; GET returns `email_confirmed`, `created_at` | ✅ |
| 20 | Google flow: FR = frontend code exchange + "ExternalLoginInfo"; §5.3 = backend callback; §8.1 = `idToken`; error 401 vs 400 | Single flow: Google Identity Services **ID token** posted to `/auth/google`. Invalid token is 401 in the FR, §8.1 and App. B (`AUTH_GOOGLE_TOKEN_INVALID`). The 400 remains only for "profile missing email" | ✅ |
| 21 | Refresh token in body, no cookie (§5.2) vs cookie attributes (NFR-SEC-005) vs "localStorage/cookie" (FR-AUTH-005) | All via HttpOnly cookies. `SameSite=Lax` in CONS-004 and NFR-SEC-005 (Strict explicitly rejected) | ✅ |
| 21b | Password rule: FR-AUTH-001 omits lowercase, NFR-SEC-001 requires it | Unchanged. FR-AUTH-001 still lists "1 uppercase, 1 digit, 1 special" only | ✅ fixed (see round 2) |

## 6. Status codes and error semantics

| # | Original | Current | Status |
| - | -------- | ------- | ------ |
| 22 | Validation: 422 in all FRs vs 400 in §8 / App. A / `VALIDATION_ERROR` | `VALIDATION_ERROR` and App. A are now **422**. Leftover: §8.2 `POST /categories` and §8.5/§8.6 rows still list "400" alongside 422 | ✅ fixed (see round 2) |
| 23 | Concurrency conflict: 409 (FR-RCP-004) vs 422 (App. A/B) | **409** everywhere (App. A, `RECIPE_CONCURRENCY_CONFLICT`). Missing/invalid `If-Match` → 422 | ✅ |
| 24 | Recipe slug collision: 409 (FR-RCP-003) vs "auto-suffix" (App. B, FR-CAT-003); slug mutability unclear | **Still open.** FR-RCP-003 A3 returns 409 while `RECIPE_SLUG_EXISTS` says auto-suffix. FR-RCP-004's status list still mentions "slug trùng" even though that endpoint no longer changes the slug. Good news: slug is now explicitly immutable via FR-RCP-004 | ✅ fixed (see round 2) |

## 7. Availability and infrastructure

| # | Original | Current | Status |
| - | -------- | ------- | ------ |
| 25 | Redis down: system continues (§2.6.2, NFR-REL-002) vs `/health/ready` fails when Redis down (FR-OBS-001) | Split into 3 Redis instances. Rate Limit Redis is fail-open and excluded from readiness (resolved). **But Cache Redis down is still graceful-degrade in §2.6.2 / NFR-REL-002 and also fails readiness, so Nginx stops routing.** | ✅ fixed (see round 2) |
| 26 | Hangfire "in-process, jobs lost" (§2.6.2) vs persisted in PG with multiple workers | Replaced by Redis Job Queue + standalone workers + DLQ. §2.6.2 now says `noeviction` protects enqueued jobs | ✅ |
| 26b | Browser minimums: Chrome 90 / Firefox 88 / Safari 14 (§2.4.3) vs 112 / 113 / 16 (§5.4) | Unchanged | ✅ fixed (see round 2) |
| 26c | Prod disk min 20 GB (§2.4.1) vs 50 GB (§5.4) | Unchanged | ✅ fixed (see round 2) |

## 8. Requirement vs data model / API drift

| # | Original | Current | Status |
| - | -------- | ------- | ------ |
| 27a | Ingredient `quantity > 0` and `unit` required (FR) vs both nullable (Ch.7) | Co-nullable rule (both null or both set) in FR-RCP-009, Ch.7 CHECK, §8.6, App. A/B | ✅ |
| 27b | `instructions` optional (FR) vs NOT NULL (Ch.7) | Field removed from both | ✅ |
| 27c | Step: no `title` in FR vs mandatory in Ch.7/§8.5; `DurationMinutes` vs `TimerMinutes`; client vs server `stepNumber` | `title` mandatory, `duration_minutes`, `step_number` server-assigned. Consistent in FR, Ch.7, §8.5 | ✅ |
| 27d | `cookTime > 0` (FR-RCP-003) vs `>= 0` "no cook" (Ch.7) | Unchanged | ✅ fixed (see round 2) |
| 27e | Category name 2–50 (FR) vs `varchar(100)`; ingredient name 1–100 vs `varchar(200)` | Unchanged. DB limits are looser than validation, which is harmless but still two numbers | ⚠️ |
| 28 | Difficulty Easy/Medium/Hard (FR) vs enum incl. Expert | Unchanged. FR doesn't enumerate values; Ch.7 still has `expert` | ✅ fixed (see round 2) |
| 29 | Category `imageUrl`/`orderIndex` in Ch.7/§8.2 but not in FR | FR-CAT-001/003/004 now include `image_url`, `order_index` | ✅ |
| 30a | Set-primary endpoint: `PATCH …/images/{id}/primary` (FR) vs `PATCH …/images/{id}` (§8.4) | **Unchanged.** FR-RCP-008 still uses `/primary`; §8.4 still lists the generic PATCH | ✅ fixed (see round 2) |
| 30b | Upload accepted `isPrimary` (§8.4) vs "first image is auto-primary" | `is_primary` removed from the upload request | ✅ |
| 31a | `sort=-createdAt` (FR) vs `sortBy`+`sortOrder` (§8) | `sort=-created_at` everywhere | ✅ |
| 31b | `minServings` filter only in the summary FR | Dropped | ✅ |
| 31c | Response wrapper `{items,total_count,…}` (FR) vs `{data, meta}` (§5.2, §8) | §8 now matches the FR (`items`, `total_count`…). **§5.2 "Response Format" still shows `{data, meta}`** | ✅ fixed (see round 2) |
| 31d | Default `page_size` 12 vs §8 example 10 | Unchanged (defaults 12 in FR, `page_size=10` in §8 examples) | ✅ fixed (see round 2) |

## 9. Minor

| # | Original | Current | Status |
| - | -------- | ------- | ------ |
| 32 | §1.2.3 puts ratings out of scope, NFR-SEO-001 promises star-rating snippets | Star-rating wording removed from NFR-SEO-001 | ✅ |

---

## Round 2: what was changed to close the open items

All SRS edits are in `docs/srs.md`; the only code change is the health check.

| # | Decision | SRS change | Code change |
| - | -------- | ---------- | ----------- |
| N1 | Search is trigram on `title` only (ADR-0008) | Removed `tsvector`/`search_vector` from §1.2.2, §6.1, §7.2 (replaced with the `idx_recipe_title_trgm_gin` row), NFR-SCALE-002 and the glossary | none (model already has only the trigram index) |
| 25 | Cache Redis is an optimisation, so it must not take an instance out of rotation | FR-OBS-001, §8.7, App. A: `/health/ready` checks the database only; `/health` no longer lists Cache Redis | `GetReadinessHandler` checks DB only; `HealthRepository.check_cache_redis` and the `cache_redis` entry removed; tests updated and a regression test added (574 passed, ruff and import-linter clean) |
| 24 | Recipe slug collisions auto-suffix (what the code already does) | FR-RCP-003 A3 and status list: no 409. FR-RCP-004 409 is concurrency only. `RECIPE_SLUG_EXISTS` removed from App. B | none |
| 16 | Email verification is out of scope for 1.0.0 | §1.2.3 lists it; §2.3 and `users.email_confirmed` say the flag is stored but gates nothing | none |
| 17a/b | Keep 423 and document it; inactive accounts get the generic 401 (what the code does) | FR-AUTH-002 A2/A2b with the accepted trade-off; 423 added to §8.1 (login, google), App. A and `AUTH_ACCOUNT_LOCKED` in App. B; `AUTH_ACCOUNT_DISABLED` removed | none |
| 6/8/30a/31c | §8 follows the FRs and the code | §8.3 `/unarchive` row and visibility wording; §8.4 `/primary` endpoint; §5.2 response format; examples use `page_size=12` | none |
| 21b | Password rule follows FR-AUTH-001 and the code | NFR-SEC-001 no longer requires a lowercase letter | none |
| 27d | API requires `cook_time_minutes > 0`, DB allows 0 | Data-model note | none |
| 28 | Difficulty values listed | FR-RCP-001 lists `easy, medium, hard, expert` | none |
| 22 | Stray 400s | Removed from §8.2, §8.5, §8.6 | none |
| 26b/c | Browser and disk minimums | §5.4 now matches §2.4 | none |

## Round 3: Appendix B error codes implemented

The code only emitted `RATE_LIMIT_EXCEEDED`; Appendix B listed 20 codes. Added `ErrorCode` (`errors.py`) and set `code=` on the matching raises; the problem response carries it as the `code` member (the SRS wrongly said `type`, now corrected).

| Group | Codes now emitted |
| ----- | ----------------- |
| Auth | `AUTH_EMAIL_EXISTS`, `AUTH_INVALID_CREDENTIALS`, `AUTH_TOKEN_EXPIRED`, `AUTH_TOKEN_INVALID`, `AUTH_REFRESH_TOKEN_EXPIRED`, `AUTH_REFRESH_TOKEN_REVOKED`, `AUTH_GOOGLE_TOKEN_INVALID`, `AUTH_ACCOUNT_LOCKED` |
| Recipe | `RECIPE_NOT_FOUND`, `RECIPE_FORBIDDEN`, `RECIPE_PUBLISH_INCOMPLETE`, `RECIPE_CONCURRENCY_CONFLICT`, `INGREDIENT_QUANTITY_UNIT_MISMATCH` |
| Category | `CATEGORY_NOT_FOUND`, `CATEGORY_NAME_EXISTS`, `CATEGORY_DELETE_HAS_RECIPES` |
| File / common | `FILE_MIME_INVALID`, `FILE_SIZE_EXCEEDED`, `VALIDATION_ERROR`, `RATE_LIMIT_EXCEEDED` |

Not coded on purpose: errors with no Appendix B entry (missing cookie, unknown refresh token, inactive account, child-resource 404s such as step/ingredient/image, empty file, admin-role 403s).
