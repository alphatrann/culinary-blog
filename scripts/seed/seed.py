"""Seed 20 categories and 100 published recipes with real photos.

Prereqs: `docker compose -f compose.development.yml up -d`, `uv run alembic upgrade head`, and
`uv run python scripts/seed/fetch_images.py` (downloads the photos + manifest.json).

Run: uv run python scripts/seed/seed.py [--reset]
Idempotent: existing categories / recipes (matched by slug) are left alone. `--reset` first deletes the seeded
author's recipes and all categories (hard delete, dev data only).
"""

import asyncio
import io
import json
import random
import re
import sys
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from data_01 import RECIPES as R1
from data_02 import RECIPES as R2
from data_03 import RECIPES as R3
from data_04 import RECIPES as R4
from data_05 import RECIPES as R5
from dishes import CATALOGUE
from minio import Minio
from minio.error import S3Error
from sqlalchemy import delete, select

from categories import DESCRIPTIONS
from culinary_blog.auth.models import User
from culinary_blog.auth.security import PasswordHasher
from culinary_blog.categories.models import Category
from culinary_blog.categories.slug import slugify
from culinary_blog.config import get_settings
from culinary_blog.database.session import async_session_factory, engine
from culinary_blog.recipes.enums import RecipeDifficulty, RecipeStatus
from culinary_blog.recipes.models import Recipe, RecipeImage, RecipeIngredient, RecipeStep

HERE = Path(__file__).parent
AUTHOR_EMAIL = "seed.author@culinary.local"
AUTHOR_PASSWORD = "SeedAuthor#2026"
RECIPES = {r["title"]: r for r in [*R1, *R2, *R3, *R4, *R5]}
QTY = re.compile(r"^(\d+(?:[.,]\d+)?|\d+/\d+)\s+(.+)$")


def parse_quantity(raw: str) -> Decimal:
    raw = raw.replace(",", ".")
    if "/" in raw:
        numerator, denominator = raw.split("/")
        return (Decimal(numerator) / Decimal(denominator)).quantize(Decimal("0.001"))
    return Decimal(raw)


def parse_ingredients(block: str) -> list[dict]:
    result = []
    for index, line in enumerate(filter(None, (ln.strip() for ln in block.strip().splitlines()))):
        parts = [p.strip() for p in line.split("|")]
        qty_unit, name, note = (parts + ["", ""])[:3]
        match = QTY.match(qty_unit)
        quantity, unit = (parse_quantity(match.group(1)), match.group(2)) if match else (None, None)
        result.append({"name": name, "quantity": quantity, "unit": unit, "notes": note or None, "order_index": index})
    return result


def parse_steps(block: str) -> list[dict]:
    result = []
    for number, line in enumerate(filter(None, (ln.strip() for ln in block.strip().splitlines())), start=1):
        parts = [p.strip() for p in line.split("|")]
        title, description = parts[0], parts[1]
        minutes = int(parts[2]) if len(parts) > 2 and parts[2] else None
        result.append({"step_number": number, "title": title, "description": description, "duration_minutes": minutes})
    return result


def validate() -> None:
    catalogue_titles = [title for _, recipes in CATALOGUE for title, _ in recipes]
    assert len(CATALOGUE) == 20 and len(catalogue_titles) == 100, "expected 20 categories x 5 recipes"
    assert set(catalogue_titles) == set(RECIPES), f"data mismatch: {set(catalogue_titles) ^ set(RECIPES)}"
    assert set(DESCRIPTIONS) == {name for name, _ in CATALOGUE}
    for title, recipe in RECIPES.items():
        ingredients, steps = parse_ingredients(recipe["ing"]), parse_steps(recipe["steps"])
        assert len(ingredients) >= 10, f"{title}: {len(ingredients)} ingredients"
        assert len(steps) >= 5, f"{title}: {len(steps)} steps"
        assert len(title) >= 5 and recipe["cook"] > 0, title
        assert all(len(i["name"]) <= 100 for i in ingredients), title
        assert all(len(s["description"]) <= 2000 for s in steps), title


class ImageStore:
    """Uploads photos to MinIO as `{folder}/{uuid4()}{ext}` and returns their public URLs (FR-FILE-001)."""

    def __init__(self) -> None:
        settings = get_settings()
        self._bucket = settings.minio_bucket_name
        self._base = f"{'https' if settings.minio_secure else 'http'}://{settings.minio_endpoint}/{self._bucket}"
        self._client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )

    def ensure_bucket(self) -> None:
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{self._bucket}/*"],
                }
            ],
        }
        self._client.set_bucket_policy(self._bucket, json.dumps(policy))

    def upload(self, path: Path, folder: str) -> str:
        key = f"{folder}/{uuid.uuid4()}{path.suffix.lower()}"
        data = path.read_bytes()
        self._client.put_object(self._bucket, key, io.BytesIO(data), len(data), content_type="image/jpeg")
        return f"{self._base}/{key}"


async def get_or_create_author(session) -> User:
    user = (await session.execute(select(User).where(User.email == AUTHOR_EMAIL))).scalar_one_or_none()
    if user:
        return user
    user = User(
        email=AUTHOR_EMAIL,
        password_hash=await PasswordHasher().hash(AUTHOR_PASSWORD),
        display_name="Bếp Việt",
        bio="Tài khoản tác giả dữ liệu mẫu cho môi trường phát triển.",
        roles=["author", "admin"],
        email_confirmed=True,
    )
    session.add(user)
    await session.flush()
    return user


async def reset(session, author: User) -> None:
    recipe_ids = select(Recipe.id).where(Recipe.author_id == author.id)
    for model in (RecipeStep, RecipeIngredient, RecipeImage):
        await session.execute(delete(model).where(model.recipe_id.in_(recipe_ids)))
    await session.execute(delete(Recipe).where(Recipe.author_id == author.id))
    await session.execute(delete(Category))


async def main() -> None:
    validate()
    manifest = json.loads((HERE / "manifest.json").read_text("utf-8"))
    store = ImageStore()
    store.ensure_bucket()
    rng = random.Random(2026)
    now = datetime.now(UTC)
    counter = 0
    created_recipes = 0

    async with async_session_factory() as session:
        author = await get_or_create_author(session)
        if "--reset" in sys.argv:
            await reset(session, author)
            await session.flush()

        for category_order, (category_name, dishes) in enumerate(CATALOGUE):
            category = (
                await session.execute(select(Category).where(Category.slug == slugify(category_name)))
            ).scalar_one_or_none()
            first_photo = HERE / "images" / manifest[f"recipe-{counter + 1:03d}"]["file"]
            if not category:
                category = Category(
                    name=category_name,
                    slug=slugify(category_name),
                    description=DESCRIPTIONS[category_name],
                    image_url=store.upload(first_photo, "categories"),
                    order_index=category_order,
                )
                session.add(category)
                await session.flush()

            for title, _ in dishes:
                counter += 1
                slug = slugify(title)
                exists = (await session.execute(select(Recipe.id).where(Recipe.slug == slug))).first()
                if exists:
                    continue
                data = RECIPES[title]
                photo = HERE / "images" / manifest[f"recipe-{counter:03d}"]["file"]
                credit = manifest[f"recipe-{counter:03d}"]
                recipe = Recipe(
                    title=title,
                    slug=slug,
                    description=data["desc"],
                    prep_time_minutes=data["prep"],
                    cook_time_minutes=data["cook"],
                    servings=data["serv"],
                    difficulty=RecipeDifficulty(data["lvl"]),
                    status=RecipeStatus.PUBLISHED,
                    category_id=category.id,
                    author_id=author.id,
                    published_at=now - timedelta(days=rng.randint(0, 90), hours=rng.randint(0, 23)),
                    **{
                        f"nutrition_{name}": Decimal(str(value))
                        for name, value in zip(
                            ("calories", "protein", "carbohydrates", "fat", "fiber", "sodium"), data["nut"], strict=True
                        )
                    },
                )
                session.add(recipe)
                await session.flush()
                session.add_all(RecipeIngredient(recipe_id=recipe.id, **i) for i in parse_ingredients(data["ing"]))
                session.add_all(RecipeStep(recipe_id=recipe.id, **s) for s in parse_steps(data["steps"]))
                session.add(
                    RecipeImage(
                        recipe_id=recipe.id,
                        original_url=store.upload(photo, "recipes"),
                        alt_text=f"{title} - ảnh: {credit['author'] or 'Wikimedia Commons'} ({credit['license']})"[
                            :200
                        ],
                        is_primary=True,
                        order_index=0,
                    )
                )
                created_recipes += 1

        await session.commit()
    await engine.dispose()
    print(f"Seeded {created_recipes} new recipes. Author login: {AUTHOR_EMAIL} / {AUTHOR_PASSWORD}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except S3Error as exc:
        sys.exit(f"MinIO error: {exc}")
