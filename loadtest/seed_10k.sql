-- SRS scale (CONS/assumptions): 10,000 recipes, 50 categories. Needs an existing user (register seed.author@example.com
-- through the API first so it has a real Argon2 hash). Columns are independent (random), unlike i%80 / i%4 patterns.
-- Run: psql ... -f loadtest/seed_10k.sql   (idempotent guard: aborts if recipes already exist)
DO $$ BEGIN IF (SELECT count(*) FROM recipes) > 0 THEN RAISE EXCEPTION 'recipes not empty'; END IF; END $$;

INSERT INTO categories (name, slug, description, order_index)
SELECT 'Danh mục ' || g, 'danh-muc-' || g, 'Mô tả danh mục ' || g, g FROM generate_series(1, 50) g;

WITH dishes(d) AS (VALUES ('Phở bò'),('Bún chả'),('Gà nướng'),('Cơm tấm'),('Bánh mì'),('Canh chua'),('Thịt kho'),
  ('Gỏi cuốn'),('Chè đậu xanh'),('Xôi gấc'),('Bún riêu'),('Cá kho tộ'),('Mì Quảng'),('Bánh xèo'),('Lẩu thái')),
 adj(a) AS (VALUES ('truyền thống'),('cay'),('chay'),('nhanh gọn'),('kiểu Hà Nội'),('kiểu miền Tây'),('đặc biệt'),('dễ làm'))
INSERT INTO recipes (title, slug, description, prep_time_minutes, cook_time_minutes, servings, difficulty, status,
                     category_id, author_id, published_at, created_at, nutrition_calories, nutrition_protein)
SELECT (SELECT d FROM dishes OFFSET (g % 15) LIMIT 1) || ' ' || (SELECT a FROM adj OFFSET ((g * 7 + floor(random()*8)::int) % 8) LIMIT 1) || ' #' || g,
       'recipe-' || g,
       'Công thức số ' || g || ': ' || repeat('nguyên liệu tươi, nêm nếm vừa ăn, ', 8),
       5 + floor(random()*40)::int, floor(random()*120)::int, 1 + floor(random()*8)::int,
       1 + floor(random()*4)::int,
       CASE WHEN random() < 0.85 THEN 1 WHEN random() < 0.7 THEN 0 ELSE 2 END,
       (SELECT id FROM categories ORDER BY id OFFSET (abs(hashtext(g::text)) % 50) LIMIT 1),  -- refers to g: evaluated per row
       (SELECT id FROM users WHERE email = 'seed.author@example.com'),
       now() - (random() * interval '365 days'), now() - (random() * interval '365 days'),
       round((100 + random()*700)::numeric, 2), round((random()*40)::numeric, 2)
FROM generate_series(1, 10000) g;
UPDATE recipes SET published_at = NULL WHERE status <> 1;

INSERT INTO recipe_steps (recipe_id, step_number, title, description, duration_minutes)
SELECT r.id, s, 'Bước ' || s, repeat('Thực hiện cẩn thận. ', 6), 5 + (s * 3) FROM recipes r, generate_series(1, 4 + (abs(hashtext(r.id::text)) % 4)) s;
INSERT INTO recipe_ingredients (recipe_id, name, quantity, unit, order_index)
SELECT r.id, 'Nguyên liệu ' || i, 1 + (i % 5), 'g', i FROM recipes r, generate_series(0, 5 + (abs(hashtext(r.id::text)) % 5)) i;
ANALYZE;
SELECT count(*) recipes, count(*) FILTER (WHERE status = 1) published FROM recipes;
