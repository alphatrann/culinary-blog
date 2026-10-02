-- EXPLAIN (ANALYZE, BUFFERS) for the hot read queries, shaped like the SQL the API emits (repository.py).
-- Run: docker exec -i <postgres-container> sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < loadtest/explain.sql
\set cat '(SELECT id FROM categories ORDER BY slug LIMIT 1)'

\echo '### 1. Guest list, newest first (GET /recipes)'
EXPLAIN (ANALYZE, BUFFERS) SELECT id, title, slug, description, prep_time_minutes, cook_time_minutes, servings, difficulty,
  status, author_id, published_at FROM recipes WHERE is_deleted IS false AND status = 1
  ORDER BY created_at DESC, id LIMIT 12;

\echo '### 2. Guest list, category + difficulty filter'
EXPLAIN (ANALYZE, BUFFERS) SELECT id, title, slug, description, prep_time_minutes, cook_time_minutes, servings, difficulty,
  status, author_id, published_at FROM recipes WHERE is_deleted IS false AND status = 1
  AND category_id = :cat AND difficulty = 2 ORDER BY created_at DESC, id LIMIT 12;

\echo '### 3. Total count for a category (pagination total)'
EXPLAIN (ANALYZE, BUFFERS) SELECT count(*) FROM recipes WHERE is_deleted IS false AND status = 1 AND category_id = :cat;

\echo '### 4. Non-admin list (published OR own)'
EXPLAIN (ANALYZE, BUFFERS) SELECT id, title, slug FROM recipes WHERE is_deleted IS false
  AND (status = 1 OR author_id = (SELECT id FROM users LIMIT 1)) ORDER BY created_at DESC, id LIMIT 12;

\echo '### 5. Recipe detail by slug'
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM recipes WHERE slug = (SELECT slug FROM recipes LIMIT 1) AND is_deleted IS false;

\echo '### 6. Search "pho" (trigram GIN, word_similarity)'
EXPLAIN (ANALYZE, BUFFERS) SELECT id, word_similarity(f_unaccent(lower('pho')), f_unaccent(lower(title))) AS score
  FROM recipes WHERE is_deleted IS false AND status = 1 AND f_unaccent(lower(title)) %> f_unaccent(lower('pho'))
  ORDER BY score DESC, id LIMIT 12;
