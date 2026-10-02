# Load tests (k6) — M6a, NFR-PERF-001/002/004

Baseline measurements for the API at the SRS data scale (≤ 10,000 recipes, ≤ 5,000 users, ≤ 50 categories), plus the
query-plan review that decides whether we need more indexes. **Verdict: no new indexes** (see [Judgment](#judgment)).

## Run it

```bash
# 1. Seed: register seed.author@example.com through the API (real Argon2 hash), then bulk-insert 10k recipes.
docker exec -i <postgres-container> sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < loadtest/seed_10k.sql

# 2. k6 (install locally: `brew install k6`), pointed at nginx. Run it on the host, not inside the Docker VM.
k6 run -e BASE_URL=http://localhost loadtest/smoke.js     # 30 s sanity check
k6 run -e BASE_URL=http://localhost loadtest/load.js      # 100 VUs, 5 min hold (NFR-PERF-002)
k6 run -e BASE_URL=http://localhost loadtest/stress.js    # 100 → 400 VUs in steps; -e STEPS=100,200 to pick steps

# 3. Query plans
docker exec -i <postgres-container> sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < loadtest/explain.sql
```

`loadtest/run-baseline.sh` runs all three k6 scripts and writes the console output to `results/`.
Raw outputs of the run below are in [`results/`](results/): `smoke.txt`, `load.txt`, `stress.txt`, `explain-analyze.txt`.

## Methodology

- **Stack:** compose stack behind nginx, API with 2 uvicorn workers, 2 CPU / 2 GB Docker VM (the SRS reference box).
  No cache and no rate limiter yet (M6b), so this is the **uncached** path.
- **Data:** `seed_10k.sql` — 10,000 recipes (8,491 published), 50 categories (168–228 recipes each), random difficulty /
  cook time / status, 4–7 steps and 6–10 ingredients per recipe.
- **Traffic mix** (`lib.js`): guest list 25%, logged-in non-admin list 10% (`status = published OR author_id = me`),
  recipe detail 25%, categories 10%, category detail 10%, search 15%, `/auth/me` 5%. Lists use random filters, sorts
  and pages (mostly 1–3, some up to 100). Each VU logs in once (login is measured, but not a throughput path: the SRS
  caps auth at 10 req/min/IP).
- **Pass criteria** (NFR-PERF-001, per endpoint): p50 < 150 ms, p95 < 500 ms, p99 < 1000 ms, errors < 1%.
- **Scripts:** `smoke` (2 VUs), `load` (ramp to 100 VUs, hold 5 min, 0.5–2.5 s think time), `stress` (fixed 90 s steps
  of 100 / 150 / 200 / 300 / 400 VUs, 0.2–1.2 s think time, so a stress VU sends ~2.2× the requests of a load VU).
- **Stress caveat:** the 2 GB Docker VM cannot also hold Tempo's span ingestion at these rates (Tempo was OOM-killed
  and API workers restarted), so stress ran with Tempo and the OTel collector stopped (the API then logs OTLP export retries, a small extra cost that makes stress numbers slightly pessimistic). Smoke and load ran with tracing on.
- **Reading traces:** slow requests were inspected in Grafana → Tempo (span per SQL statement) to see where time goes.

## How to read `EXPLAIN (ANALYZE, BUFFERS)`

`explain.sql` runs the hot queries with the same shape the repositories emit. Things to look at:

| Output | Meaning |
|---|---|
| `Seq Scan` | Reads the whole table. Fine for a few thousand rows, a problem at millions. |
| `Index Scan` / `Bitmap Index Scan` | Uses an index to find rows. `Bitmap Heap Scan` then fetches those rows. |
| `Sort Method: top-N heapsort` | `ORDER BY … LIMIT n` keeps only the best n rows in memory — cheap. |
| `actual time=a..b rows=r` | Real time (ms) to first/last row and rows returned by that step. |
| `Execution Time` | Total time of the statement. This is the number to compare against the latency budget. |
| `Buffers: shared hit/read` | 8 KB pages served from cache (`hit`) or disk (`read`). |
| estimated `rows=` vs actual `rows=` | Big mismatches mean stale statistics (`ANALYZE`) or correlated columns. |

## Results

### Query plans (10k recipes, `results/explain-analyze.txt`)

| Query | Plan | Time |
|---|---|---|
| Guest list, newest first | Seq scan of 8.5k rows + top-N sort | 4.6 ms |
| List with category + difficulty | Bitmap AND of `ix_recipes_category_id` and `ix_recipes_difficulty` | 0.3 ms |
| Category total (pagination) | `ix_recipes_category_id` | 0.2 ms |
| Non-admin list (published OR own) | Seq scan + top-N sort | 2.9 ms |
| Recipe detail by slug | `ix_recipes_slug` | 0.03 ms |
| Search `pho` | `idx_recipe_title_trgm_gin` | 5.7 ms |

### Load: 100 VUs, 5 min — 22,948 requests, 59 req/s, 0% errors (p50 / p95 / p99, ms)

| Endpoint | p50 | p95 | p99 |
|---|---|---|---|
| list (guest) | 7 | 14 | 20 |
| list (non-admin) | 7 | 13 | 17 |
| recipe detail | 5 | 11 | 18 |
| categories | 7 | 12 | 19 |
| category detail | 6 | 12 | 20 |
| search | 16 | 30 | 39 |
| `/auth/me` | 3 | 6 | 10 |
| login (Argon2) | 90 | 155 | 191 |

All endpoints pass NFR-PERF-001/002 by more than an order of magnitude. Smoke (2 VUs): 0% errors, same shape.

### Stress: all endpoints together, fixed steps

| VUs | p50 (ms) | p95 (ms) | p99 (ms) | errors |
|---|---|---|---|---|
| 100 | 9 | 250 | 1113 | 0% |
| 150 | 16 | 732 | 1428 | 0% |
| 200 | 216 | 1675 | 3275 | 0% |
| 300 | 827 | 2711 | 3835 | 0.2% |
| 400 | 1628 | 3489 | 42585 | 1.9% |

> **Read the 400-VU row with care.** Its p99 (~43 s) and 1.9% errors are not steady-state latency: about 200 requests
> failed within one second of the step starting (`dial tcp 127.0.0.1:80: connection reset by peer`, see
> `results/stress.txt`) because 400 VUs opened connections at the same instant and Docker Desktop's port forward
> reset them; the ~40 s tail is most likely TCP connect retries after those resets. The typical request at that step
> is the p50/p95 shown. The server logged no crash, restart or nginx error at that moment. Steps start without a ramp,
> so treat 300+ VUs as "clearly saturated", not as exact numbers.

**Knee: ~100–150 stress VUs (≈ 220–330 load-test users, ~150–190 req/s).** Above it latency climbs with load
(queueing) and connections start dropping. Every endpoint degrades together, including `/auth/me` (no DB call), so the
limit is API CPU on the 2-vCPU box, not the database.

## Judgment

**Do not add indexes now.**

- Every hot query runs in under 6 ms at 10k rows; the worst ones are a seq scan of ~8.5k rows plus a top-N sort.
  The latency budget is 500 ms, and p95 at the 100-user target is 11–30 ms.
- Where an index is selective, the planner already uses one (`category_id`, `slug`, trigram GIN for search).
- Traces of slow requests under stress show SQL spans of a few ms; the time is spent queueing for CPU and in
  round trips, not in query execution.
- Extra indexes cost writes and disk for no measurable gain at this volume.

**Revisit when the table is ~100× larger.** A local test with 5M rows showed the same list queries seq-scanning for
~0.5 s and `count(*)` for seconds; at that size add partial indexes on `(created_at DESC, id) WHERE status = 1 AND
is_deleted = false` and `(category_id, created_at DESC, id)`, and stop computing exact totals.

## What we changed because of this run

- Reads use an AUTOCOMMIT session on the shared pool (no `BEGIN`/`ROLLBACK` per query) and `pool_pre_ping` is off by
  default (it cost 3 round trips per checkout). Trade-off: after a Postgres restart the first request on a stale
  connection can fail once; set `DB_POOL_PRE_PING=true` to restore the old behaviour. Category detail went from ~10 DB
  round trips to 3.
- Guest category detail reuses the page total instead of running a second count.
- nginx re-resolves the API address (it kept a stale IP after an API restart → 502) and has more workers/connections.
- OTel collector: replaced the removed `loki` exporter with `otlphttp/loki`.

Next: M6b (cache-aside, hit rate ≥ 80%) is the lever for the CPU-bound knee; re-run these scripts afterwards.
