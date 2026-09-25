# ADR-0008: pg_trgm word-similarity search over recipe titles, not tsvector/ts_rank

## Status

Accepted

## Context

- FR-SRCH-001 originally specified a `tsvector` `search_vector` generated column over `title`/`description`,
  trigger-maintained, queried with `to_tsquery('vietnamese', ...)` and ranked by `ts_rank()`.
- PostgreSQL ships no built-in `vietnamese` text search configuration (no Vietnamese stemmer/dictionary), so that
  design requires hand-building a custom `TEXT SEARCH CONFIGURATION` — a nontrivial linguistic undertaking, and one
  `to_tsquery` still tokenizes on whitespace/punctuation rather than doing substring/typo-tolerant matching.
- The scope actually needed (and already migrated ahead of this ADR, see `migrations/versions/21e3398d1493_*`) is
  simpler: diacritic-insensitive, typo-tolerant matching on recipe **titles**, e.g. `pho` should find `Phở Bò Hà Nội`.
  `pg_trgm` trigram similarity, combined with the `unaccent` extension, does this directly with no custom
  dictionary — `unaccent` folds `ơ`/`ở`/`ố`/... to `o`, and trigram indexes are inherently substring/fuzzy tolerant.

## Decision

- Search runs against a GIN index on the functional expression `f_unaccent(lower(title))` (`gin_trgm_ops`), not a
  `search_vector` column. `f_unaccent` wraps `unaccent()` so it can be marked `IMMUTABLE` and used in an index.
- Matching uses pg_trgm's `word_similarity` via the indexed `%>` operator: `f_unaccent(lower(title)) %> f_unaccent(lower(:q))`.
  `word_similarity` looks for the best-matching word-sized extent of the (longer) title against the (shorter) query,
  which is what makes short/partial queries like `pho` score well against long titles — plain `similarity()`/`%`
  would compare the two full strings and penalize the length mismatch.
- `relevance_score` in the API response is `word_similarity(query, title)`, `0..1`, descending.
- Scope is **title only** — descriptions are not indexed or searched. If search needs to cover descriptions later,
  that is a separate index/ADR, not a retrofit of this one.
- `docs/srs.md` FR-SRCH-001 is updated to describe this trigram-based design instead of the original
  tsvector/ts_rank one, per the "update the SRS rather than silently diverge" rule in `CLAUDE.md`.

## Consequences

- No custom Vietnamese text search dictionary to build or maintain; `unaccent` + trigram gets diacritic-insensitive,
  typo-tolerant matching with two off-the-shelf extensions.
- Trigram similarity degrades on very short queries (1–2 trigrams) and on titles shorter than the query; the
  endpoint enforces `q` ≥ 2 characters, and very short titles may simply not have enough trigram signal to match
  a longer query, which is an acceptable trade-off for a recipe blog's titles.
- Query-result caching (ADR-0003, 5min TTL) is deliberately **not** implemented in M5b — it is scoped to M6b (Cache
  layer) alongside the category/recipe cache-aside work, so this endpoint always hits Postgres for now.
- **Revisit trigger:** if search needs to rank by more than title match (popularity, recency) or cover
  ingredients/description, the ranking formula and indexed columns both need revisiting together.
