import uuid

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlmodel import col, select

from culinary_blog.categories.models import Category
from culinary_blog.errors import ConflictError
from culinary_blog.recipes.models import Recipe, RecipeIngredient, RecipeStep

UNIQUE_VIOLATION = "23505"  # PostgreSQL SQLSTATE


class RecipeRepository:
    """The only place that runs recipe queries."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def category_exists(self, category_id: uuid.UUID) -> bool:
        async with self._session_factory() as session:
            result = await session.execute(
                select(func.count())
                .select_from(Category)
                .where(Category.id == category_id, col(Category.is_deleted).is_(False))
            )
            return result.scalar_one() > 0

    # The uniqueness check includes soft-deleted rows: the unique constraint does too.
    async def slug_taken(self, slug: str) -> bool:
        async with self._session_factory() as session:
            result = await session.execute(select(func.count()).select_from(Recipe).where(Recipe.slug == slug))
            return result.scalar_one() > 0

    async def add(self, recipe: Recipe, steps: list[RecipeStep], ingredients: list[RecipeIngredient]) -> None:
        """Persist a recipe with its steps and ingredients in one transaction."""
        async with self._session_factory() as session:
            session.add(recipe)
            await session.flush()
            session.add_all([*steps, *ingredients])
            try:
                await session.commit()
            except IntegrityError as exc:
                if getattr(exc.orig, "sqlstate", None) != UNIQUE_VIOLATION:
                    raise
                raise ConflictError("A recipe with this slug already exists") from exc
