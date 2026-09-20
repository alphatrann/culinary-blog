import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import ColumnElement, func, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlmodel import col, or_, select

from culinary_blog.auth.models import User
from culinary_blog.categories.models import Category
from culinary_blog.errors import ConflictError
from culinary_blog.recipes.enums import RecipeDifficulty, RecipeStatus
from culinary_blog.recipes.models import Recipe, RecipeImage, RecipeIngredient, RecipeStep

UNIQUE_VIOLATION = "23505"  # PostgreSQL SQLSTATE

_SORT_COLUMNS = {
    "created_at": col(Recipe.created_at),
    "title": col(Recipe.title),
    "cook_time_minutes": col(Recipe.cook_time_minutes),
}


@dataclass
class RecipeAggregate:
    """A recipe with everything the detail view needs, loaded together."""

    recipe: Recipe
    category: Category
    author: User
    steps: list[RecipeStep]
    ingredients: list[RecipeIngredient]
    images: list[RecipeImage]


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

    async def get_by_id(self, recipe_id: uuid.UUID) -> Recipe | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(Recipe).where(Recipe.id == recipe_id, col(Recipe.is_deleted).is_(False))
            )
            return result.scalars().first()

    async def get_children(self, recipe_id: uuid.UUID) -> tuple[list[RecipeStep], list[RecipeIngredient]]:
        """A recipe's live steps (by step_number) and ingredients (by order_index)."""
        async with self._session_factory() as session:
            return await self._load_children(session, recipe_id)

    async def get_aggregate_by_slug(self, slug: str) -> RecipeAggregate | None:
        """A live recipe by slug with its category, author, steps, ingredients and images."""
        async with self._session_factory() as session:
            head = (
                await session.execute(
                    select(Recipe, Category, User)
                    .join(Category, col(Category.id) == col(Recipe.category_id))
                    .join(User, col(User.id) == col(Recipe.author_id))
                    .where(Recipe.slug == slug, col(Recipe.is_deleted).is_(False))
                )
            ).first()
            if head is None:
                return None
            recipe, category, author = head
            steps, ingredients = await self._load_children(session, recipe.id)
            images = (
                await session.execute(
                    select(RecipeImage)
                    .where(RecipeImage.recipe_id == recipe.id, col(RecipeImage.is_deleted).is_(False))
                    .order_by(col(RecipeImage.order_index), col(RecipeImage.created_at))
                )
            ).scalars()
            return RecipeAggregate(recipe, category, author, steps, ingredients, list(images))

    async def list_visible(
        self,
        *,
        viewer_id: uuid.UUID | None,
        see_all: bool,
        category_id: uuid.UUID | None,
        difficulty: RecipeDifficulty | None,
        max_cook_time: int | None,
        sort: str,
        page: int,
        page_size: int,
    ) -> tuple[list[Recipe], int]:
        """One page of recipes plus the total. Non-admins see published + their own."""
        conditions: list[ColumnElement[bool]] = [col(Recipe.is_deleted).is_(False)]
        if not see_all:
            visible: list[ColumnElement[bool]] = [col(Recipe.status) == RecipeStatus.PUBLISHED]
            if viewer_id is not None:
                visible.append(col(Recipe.author_id) == viewer_id)
            conditions.append(or_(*visible))
        if category_id is not None:
            conditions.append(col(Recipe.category_id) == category_id)
        if difficulty is not None:
            conditions.append(col(Recipe.difficulty) == difficulty)
        if max_cook_time is not None:
            conditions.append(col(Recipe.cook_time_minutes) <= max_cook_time)

        sort_column = _SORT_COLUMNS[sort.removeprefix("-")]
        ordering = sort_column.desc() if sort.startswith("-") else sort_column.asc()
        async with self._session_factory() as session:
            total = (await session.execute(select(func.count()).select_from(Recipe).where(*conditions))).scalar_one()
            result = await session.execute(
                select(Recipe)
                .where(*conditions)
                .order_by(ordering, col(Recipe.id))  # id as tie-break keeps pages stable
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            return list(result.scalars().all()), int(total)

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

    async def update(self, recipe_id: uuid.UUID, expected_version: int, values: dict[str, object]) -> Recipe | None:
        """Optimistic-concurrency update: one atomic compare-and-swap on `row_version`.

        Returns the updated recipe, or None when no live row matched both the id and `expected_version`
        (someone else changed it first, or it is gone). The check and the write are a single statement, so no
        transaction isolation beyond the default is needed.
        """
        async with self._session_factory() as session:
            result = await session.execute(
                update(Recipe)
                .where(
                    col(Recipe.id) == recipe_id,
                    col(Recipe.row_version) == expected_version,
                    col(Recipe.is_deleted).is_(False),
                )
                .values(**values, row_version=col(Recipe.row_version) + 1, updated_at=datetime.now(UTC))
                .returning(Recipe)
            )
            recipe = result.scalar_one_or_none()
            await session.commit()
            return recipe

    @staticmethod
    async def _load_children(
        session: AsyncSession, recipe_id: uuid.UUID
    ) -> tuple[list[RecipeStep], list[RecipeIngredient]]:
        steps = await session.execute(
            select(RecipeStep)
            .where(RecipeStep.recipe_id == recipe_id, col(RecipeStep.is_deleted).is_(False))
            .order_by(col(RecipeStep.step_number))
        )
        ingredients = await session.execute(
            select(RecipeIngredient)
            .where(RecipeIngredient.recipe_id == recipe_id, col(RecipeIngredient.is_deleted).is_(False))
            .order_by(col(RecipeIngredient.order_index), col(RecipeIngredient.created_at))
        )
        return list(steps.scalars().all()), list(ingredients.scalars().all())
