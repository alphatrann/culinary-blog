-- Categories the e2e specs choose from. Run once against a fresh e2e database (categories are not created by the API
-- without an admin account). Idempotent on the slug.
insert into categories (id, created_at, updated_at, is_deleted, row_version, name, slug, description, image_url, order_index)
values (gen_random_uuid(), now(), now(), false, 0, 'Món chính', 'mon-chinh', 'Các món ăn chính', null, 1)
on conflict do nothing;
