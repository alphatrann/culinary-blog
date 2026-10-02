# Load tests (k6) — M6a/M6b, NFR-PERF-001/002/003/004

Baseline numbers for the API at the SRS data size (up to 10,000 recipes, 5,000 users, 50 categories), and a look at the
query plans to decide whether we need more indexes. Short answer: we don't (see [Judgment](#judgment)).

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
  The M6a numbers below are the uncached path (no cache, no rate limiter yet). M6b results are in
  [Cache layer (M6b)](#cache-layer-m6b).
- **Data:** `seed_10k.sql` — 10,000 recipes (8,491 published), 50 categories (168–228 recipes each), random difficulty /
  cook time / status, 4–7 steps and 6–10 ingredients per recipe.
- **Traffic mix** (`lib.js`): guest list 25%, logged-in non-admin list 10% (`status = published OR author_id = me`),
  recipe detail 25%, categories 10%, category detail 10%, search 15%, `/auth/me` 5%. Lists use random filters, sorts
  and pages (mostly 1–3, some up to 100). Each VU logs in once (login is measured, but not a throughput path: the SRS
  caps auth at 10 req/min/IP).
- **Pass criteria** (NFR-PERF-001, per endpoint): p50 < 150 ms, p95 < 500 ms, p99 < 1000 ms, errors < 1%.
- **Scripts:** `smoke` (2 VUs), `load` (ramp to 100 VUs, hold 5 min, 0.5–2.5 s think time), `stress` (90 s steps, each a 10 s ramp plus
  an 80 s hold, of 100 / 150 / 200 / 300 / 400 VUs, 0.2–1.2 s think time, so a stress VU sends ~2.2× the requests of a load VU).
- **Stress caveat:** the 2 GB VM can't keep up with Tempo's span ingestion at these rates. Tempo got OOM-killed and the
  API workers restarted, so stress ran with Tempo and the OTel collector stopped. The API then logs OTLP export retries,
  which costs a little, so the stress numbers are a bit worse than they'd be otherwise. Smoke and load ran with tracing on.
- **Traces:** to see where time goes, I opened slow requests in Grafana → Tempo (one span per SQL statement).

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

Every endpoint is well inside NFR-PERF-001/002, by more than 10×. Smoke (2 VUs) looked the same, 0% errors.

### Stress: all endpoints together, stepped (each step: 10 s ramp + 80 s hold)

| VUs | p50 (ms) | p95 (ms) | p99 (ms) | max (ms) | errors |
|---|---|---|---|---|---|
| 100 | 8 | 84 | 386 | 2539 | 0% |
| 150 | 15 | 537 | 1282 | 2419 | 0% |
| 200 | 213 | 1199 | 2397 | 4828 | 0% |
| 300 | 930 | 2393 | 3870 | 5280 | 0% |
| 400 | 1450 | 2554 | 4086 | 9779 | 0.01% |

74,930 requests, ~160 req/s average, 0.004% errors overall.

The knee is around 150 stress VUs (roughly 330 load-test users, 150–190 req/s). p95 is 84 ms at 100 VUs and goes
past the 500 ms target at 150. After that latency keeps growing because requests queue up, but they still get
answered: almost no errors even at 400 VUs. All endpoints slow down together, including `/auth/me`, which never
touches the DB. So I read this as the API running out of CPU on the 2-vCPU box, not Postgres being the limit.

**What the SRS actually requires.** NFR-PERF-001/002 ask for p95 ≤ 500 ms with ≥ 100 concurrent users on this box.
That is the **Load** test above, and it passes with a large margin. The stress steps are not pass/fail: they go past the
requirement to find the limit, so missing 500 ms at 200+ VUs is expected, not an SRS violation. To compare the two
(by request rate, approximate): a stress VU sends ~2.2× the requests of a load VU, so the SRS target of 100 users is
about 45 stress VUs, the first miss at 150 VUs is ~3× the requirement, and 300–400 VUs are ~7–9× the requirement.

## Judgment

No new indexes for now.

- The hot queries all finish in under 6 ms at 10k rows. The worst are a seq scan over ~8.5k rows plus a top-N sort,
  which is fine against a 500 ms budget (p95 at the 100-user target is 11–30 ms).
- Where an index would actually help, the planner already uses one (`category_id`, `slug`, trigram GIN for search).
- Under stress the SQL spans in Tempo were a few ms each. The time goes to waiting for CPU and to DB round trips, not
  to the queries.
- More indexes would add write cost and disk for no gain I can measure at this size.

This changes at around 100× the data. I tried 5M rows locally: the list queries seq-scanned for about 0.5 s and
`count(*)` took seconds. If we ever get there, add partial indexes on `(created_at DESC, id) WHERE status = 1 AND
is_deleted = false` and `(category_id, created_at DESC, id)`, and stop computing exact totals.

## What changed because of this run

- Reads now use an AUTOCOMMIT session on the shared pool, so there's no `BEGIN`/`ROLLBACK` per query, and
  `pool_pre_ping` is off by default (it cost 3 round trips per checkout). The catch: after a Postgres restart the first
  request on a stale connection can fail once. Set `DB_POOL_PRE_PING=true` if that bothers you. Category detail went
  from about 10 DB round trips to 3.
- Guest category detail reuses the page total instead of running a second count.
- nginx re-resolves the API address (it held on to a stale IP after an API restart and returned 502) and has more
  workers and connections.
- The OTel collector config used the removed `loki` exporter; it now uses `otlphttp/loki`.

Next is M6b. Cache-aside (hit rate ≥ 80%) should help most with the CPU-bound knee, and these scripts should be re-run
after it lands.

## Cache layer (M6b)

Same stack, seed and scripts as above, API rebuilt with the cache (ADR-0010), cache flushed before each run.
TTLs lowered to 1/30 (recipes 60 s, categories 120 s, search 10 s) so a 6-minute run sees expiries; production keeps
ADR-0003's values. Uncached = rerun on the same machine (`results/load-pre-cache.txt`); cached =
`results/load-cached-ttl-lowered.txt`.

### Load: 100 VUs, 5 min (ms, uncached → cached)

| Endpoint | p50 | p95 | p99 |
|---|---|---|---|
| categories | 6.9 → **2.4** | 12.0 → **4.8** | 26.1 → **8.4** |
| recipe detail | 5.4 → **2.6** | 11.1 → **7.2** | 19.5 → **12.6** |
| search | 16.1 → **3.3** | 30.8 → **20.4** | 40.2 → **31.7** |
| list (guest) | 6.7 → 6.8 | 14.2 → 13.9 | 21.5 → 21.2 |
| category detail | 6.4 → 6.6 | 12.8 → 11.8 | 21.2 → 19.3 |
| list (signed in, never cached) | 6.6 → 6.5 | 13.5 → 13.4 | 22.4 → 20.0 |
| `/auth/me` | 3.0 → 3.1 | 6.0 → 6.0 | 10.6 → 9.4 |
| **all** | 6.4 → **4.4** | 21.4 → **13.1** | 36.0 → **27.7** |

~59 req/s and 0% errors in both runs. At 100 users the API was already far inside NFR-PERF-001.

### Cache hit rate (`cache_requests_total`, load run)

| Tier | Hit | Stale | Miss | From cache |
|---|---|---|---|---|
| categories | 2,276 | – | 3 | 99.9% |
| recipe detail | 4,555 | 600 | 495 | 91.2% |
| search | 2,229 | – | 1,286 | 63.4% |
| category page (guest) | 22 | – | 18 | 54% |
| recipe list (guest) | 14 | – | 102 | 12% |
| **total** | 9,096 | 600 | 1,904 | **83.6%** (78.4% fresh hits only) |

- Meets NFR-PERF-003 (≥ 80%), counting stale-while-revalidate responses as served from cache.
- Low tiers reflect k6's random filters/pages against 10–60 s TTLs, not the cache. Signed-in lists and `/auth/me`
  bypass it.

### Stress: latest run (ms, uncached → cached)

Plain `k6 run`, Tempo and the OTel collector stopped. `results/stress-cached-ttl-lowered.txt`.

| VUs | p50 | p95 | p99 | errors |
|---|---|---|---|---|
| 100 | 8 → **4.5** | 84 → **22** | 386 → **184** | 0% → 0% |
| 150 | 15 → **5.6** | 537 → **195** | 1282 → **938** | 0% → 0.23% |
| 200 | 213 → **6.9** | 1199 → **596** | 2397 → **1430** | 0% → 0.23% |
| 300 | 930 → **23** | 2393 → **1790** | 3870 → 11280 | 0% → 0.31% |
| 400 | 1450 → **197** | 2554 → **335** | 4086 → **402** | 0.01% → 0.16% |

112,276 requests, 238 req/s (uncached: 74,930, ~160 req/s), 0.20% errors.

- 150 VUs now meets p95 < 500 ms (195 ms); 200 VUs still misses (596 ms). Spread above 200 VUs is large between runs.
- **API workers are OOM-killed at step ramp-in** (3–4 per run, 2 GB VM), which causes the errors and the 300-VU tail;
  400 VUs ramped in without a kill. Cause: every new VU logs in and Argon2 uses 64 MiB per hash (300 simultaneous
  logins: 250 → 667 MB, 31 × 502, one worker killed). Unrelated to the cache; the uncached run had the same exposure.
  Not fixed (options: cap concurrent hashes, lower `memory_cost`, stagger logins in `stress.js`).

### Not done

- Run with the real ADR-0003 TTLs.
- Stress with logins staggered or capped, to see 300 VUs without worker restarts.
