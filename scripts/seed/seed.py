"""Seed 20 categories and 100 published recipes with real photos, through the public API.

Prereqs: dev stack up (`docker compose -f compose.development.yml up -d`), migrations applied, the API running
(`uv run culinary-blog`), the image worker running (`uv run culinary-blog-image-worker`), and the photos fetched
(`uv run python scripts/seed/fetch_images.py`).

Run: uv run python scripts/seed/seed.py [--reset] [--api http://localhost:8000]

Recipes, steps, ingredients, images and publishing all go through the HTTP API, so every upload enqueues a real
`resize_image` job that the worker processes. Only two things bypass it: promoting the seed author to admin (there is
no endpoint for that) and uploading category images (there is no category upload endpoint).
`--reset` first deletes ALL recipes, categories and objects in the bucket, and clears the job queues (dev data only).
"""

import asyncio
import json
import re
import sys
import time
from decimal import Decimal
from pathlib import Path

import httpx
from data_01 import RECIPES as R1
from data_02 import RECIPES as R2
from data_03 import RECIPES as R3
from data_04 import RECIPES as R4
from data_05 import RECIPES as R5
from dishes import CATALOGUE
from minio import Minio
from sqlalchemy import delete, update
from sqlmodel import col

from categories import DESCRIPTIONS
from culinary_blog.auth.models import User
from culinary_blog.cache.redis import get_queue_redis
from culinary_blog.categories.models import Category
from culinary_blog.categories.slug import slugify
from culinary_blog.config import get_settings
from culinary_blog.database.session import async_session_factory, engine
from culinary_blog.jobs.queue import DELETE_FILE, RESIZE_IMAGE, dead_letter_queue
from culinary_blog.recipes.models import Recipe, RecipeImage, RecipeIngredient, RecipeStep
from culinary_blog.storage.minio_storage import MinioFileStorage

HERE = Path(__file__).parent
AUTHOR_EMAIL = "seed.author@example.com"
AUTHOR_PASSWORD = "SeedAuthor#2026"
RECIPES = {r["title"]: r for r in [*R1, *R2, *R3, *R4, *R5]}
QTY = re.compile(r"^(\d+(?:[.,]\d+)?|\d+/\d+)\s+(.+)$")
NUTRITION_FIELDS = ("calories", "protein", "carbohydrates", "fat", "fiber", "sodium")


def parse_quantity(raw: str) -> float:
    raw = raw.replace(",", ".")
    if "/" in raw:
        numerator, denominator = raw.split("/")
        return float((Decimal(numerator) / Decimal(denominator)).quantize(Decimal("0.001")))
    return float(raw)


def parse_ingredients(block: str) -> list[dict]:
    result = []
    for line in filter(None, (ln.strip() for ln in block.strip().splitlines())):
        parts = [p.strip() for p in line.split("|")]
        qty_unit, name, note = (parts + ["", ""])[:3]
        match = QTY.match(qty_unit)
        result.append(
            {
                "name": name,
                "quantity": parse_quantity(match.group(1)) if match else None,
                "unit": match.group(2) if match else None,
                "notes": note or None,
            }
        )
    return result


def parse_steps(block: str) -> list[dict]:
    result = []
    for line in filter(None, (ln.strip() for ln in block.strip().splitlines())):
        parts = [p.strip() for p in line.split("|")]
        step: dict[str, object] = {"title": parts[0], "description": parts[1]}
        if len(parts) > 2 and parts[2]:
            step["duration_minutes"] = int(parts[2])
        result.append(step)
    return result


def validate() -> None:
    titles = [title for _, recipes in CATALOGUE for title, _ in recipes]
    assert len(CATALOGUE) == 20 and len(titles) == 100, "expected 20 categories x 5 recipes"
    assert set(titles) == set(RECIPES), f"data mismatch: {set(titles) ^ set(RECIPES)}"
    assert set(DESCRIPTIONS) == {name for name, _ in CATALOGUE}
    for title, recipe in RECIPES.items():
        assert len(parse_ingredients(recipe["ing"])) >= 10, f"{title}: fewer than 10 ingredients"
        assert len(parse_steps(recipe["steps"])) >= 5, f"{title}: fewer than 5 steps"


async def reset() -> None:
    """Hard-delete recipes, categories and bucket objects; empty the job queues."""
    async with async_session_factory() as session:
        for model in (RecipeStep, RecipeIngredient, RecipeImage):
            await session.execute(delete(model))
        await session.execute(delete(Recipe))
        await session.execute(delete(Category))
        await session.commit()
    settings = get_settings()
    client = Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )
    removed = 0
    if client.bucket_exists(settings.minio_bucket_name):
        for obj in list(client.list_objects(settings.minio_bucket_name, recursive=True)):
            client.remove_object(settings.minio_bucket_name, obj.object_name or "")
            removed += 1
    queue = get_queue_redis()
    await queue.delete(*[q for name in (RESIZE_IMAGE, DELETE_FILE) for q in (name, dead_letter_queue(name))])
    print(f"Reset: recipes/categories deleted, {removed} objects removed, queues cleared")


async def sign_in(client: httpx.AsyncClient) -> None:
    credentials = {"email": AUTHOR_EMAIL, "password": AUTHOR_PASSWORD}
    registered = await client.post("/api/v1/auth/register", json={"display_name": "Bếp Việt", **credentials})
    if registered.status_code not in (201, 409):
        registered.raise_for_status()
    async with async_session_factory() as session:  # no endpoint grants roles: promote directly
        await session.execute(
            update(User).where(col(User.email) == AUTHOR_EMAIL).values(roles=["author", "admin"], email_confirmed=True)
        )
        await session.commit()
    (await client.post("/api/v1/auth/login", json=credentials)).raise_for_status()  # fresh token carries the roles


async def ensure_category(client: httpx.AsyncClient, storage: MinioFileStorage, order: int, name: str, photo: Path):
    existing = {c["slug"]: c for c in (await client.get("/api/v1/categories")).json()}
    if slugify(name) in existing:
        return existing[slugify(name)]["id"]
    image_url = await storage.upload(photo.read_bytes(), "categories", ".jpg", "image/jpeg")
    body = {"name": name, "description": DESCRIPTIONS[name], "image_url": image_url}
    created = await client.post("/api/v1/categories", json=body)
    created.raise_for_status()
    category_id = created.json()["id"]
    (await client.put(f"/api/v1/categories/{category_id}", json={**body, "order_index": order})).raise_for_status()
    return category_id


async def seed_recipe(client: httpx.AsyncClient, category_id: str, title: str, index: int, manifest: dict) -> bool:
    if (await client.get(f"/api/v1/recipes/{slugify(title)}")).status_code == 200:
        return False
    data = RECIPES[title]
    credit = manifest[f"recipe-{index:03d}"]
    body = {
        "title": title,
        "description": data["desc"],
        "category_id": category_id,
        "prep_time_minutes": data["prep"],
        "cook_time_minutes": data["cook"],
        "servings": data["serv"],
        "difficulty": data["lvl"],
        "nutrition": dict(zip(NUTRITION_FIELDS, data["nut"], strict=True)),
        "ingredients": parse_ingredients(data["ing"]),
        "steps": parse_steps(data["steps"]),
    }
    created = await client.post("/api/v1/recipes", json=body)
    created.raise_for_status()
    recipe_id = created.json()["id"]
    photo = HERE / "images" / credit["file"]
    alt = f"{title} - ảnh: {credit['author'] or 'Wikimedia Commons'} ({credit['license']})"[:200]
    (
        await client.post(
            f"/api/v1/recipes/{recipe_id}/images",
            files={"file": (photo.name, photo.read_bytes(), "image/jpeg")},
            data={"alt_text": alt},
        )
    ).raise_for_status()
    (await client.patch(f"/api/v1/recipes/{recipe_id}/publish")).raise_for_status()
    return True


async def wait_for_thumbnails(client: httpx.AsyncClient, slugs: list[str], timeout: int = 180) -> None:
    """Poll the API until every seeded recipe's primary image has its resized variants."""
    deadline = time.monotonic() + timeout
    pending = set(slugs)
    while pending and time.monotonic() < deadline:
        for slug in list(pending):
            images = (await client.get(f"/api/v1/recipes/{slug}")).json()["images"]
            if images and images[0]["thumbnail_url"] and images[0]["medium_url"]:
                pending.discard(slug)
        print(f"\r  resize jobs done: {len(slugs) - len(pending)}/{len(slugs)}", end="", flush=True)
        if pending:
            await asyncio.sleep(1)
    print()
    if pending:
        print(
            f"WARNING: {len(pending)} recipes still without thumbnails (is the worker running?): {sorted(pending)[:5]}"
        )


async def main() -> None:
    validate()
    api = sys.argv[sys.argv.index("--api") + 1] if "--api" in sys.argv else "http://localhost:8000"
    manifest = json.loads((HERE / "manifest.json").read_text("utf-8"))
    if "--reset" in sys.argv:
        await reset()
    storage = MinioFileStorage(get_settings())

    async with httpx.AsyncClient(base_url=api, timeout=60) as client:
        await sign_in(client)
        counter, created, slugs = 0, 0, []
        for order, (category_name, dishes) in enumerate(CATALOGUE):
            first_photo = HERE / "images" / manifest[f"recipe-{counter + 1:03d}"]["file"]
            category_id = await ensure_category(client, storage, order, category_name, first_photo)
            for title, _ in dishes:
                counter += 1
                created += await seed_recipe(client, category_id, title, counter, manifest)
                slugs.append(slugify(title))
            print(f"  [{order + 1:2d}/20] {category_name}: {counter} recipes so far")
        print(f"Created {created} recipes via the API. Waiting for the worker to resize the images...")
        await wait_for_thumbnails(client, slugs)
    await engine.dispose()
    await get_queue_redis().aclose()
    print(f"Done. Author login: {AUTHOR_EMAIL} / {AUTHOR_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(main())
