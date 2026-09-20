import uuid
from datetime import UTC, datetime

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlmodel import col, or_, select

from culinary_blog.categories.models import Category
from culinary_blog.errors import ConflictError
from culinary_blog.recipes.enums import RecipeStatus
from culinary_blog.recipes.models import Recipe

UNIQUE_VIOLATION = "23505"  # PostgreSQL SQLSTATE


class CategoryRepository:
    """The only place that runs category queries."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def list_with_recipe_counts(self) -> list[tuple[Category, int]]:
        """Every live category with its published-recipe count, ordered by name."""
        async with self._session_factory() as session:
            published = (
                select(col(Recipe.category_id), func.count().label("n"))
                .where(col(Recipe.is_deleted).is_(False), Recipe.status == RecipeStatus.PUBLISHED)
                .group_by(col(Recipe.category_id))
                .subquery()
            )
            result = await session.execute(
                select(Category, func.coalesce(published.c.n, 0))
                .outerjoin(published, published.c.category_id == Category.id)
                .where(col(Category.is_deleted).is_(False))
                .order_by(col(Category.name))
            )
            return [(category, int(count)) for category, count in result.all()]

    async def get_by_slug(self, slug: str) -> Category | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(Category).where(Category.slug == slug, col(Category.is_deleted).is_(False))
            )
            return result.scalars().first()

    async def get_by_id(self, category_id: uuid.UUID) -> Category | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(Category).where(Category.id == category_id, col(Category.is_deleted).is_(False))
            )
            return result.scalars().first()

    async def count_published_recipes(self, category_id: uuid.UUID) -> int:
        async with self._session_factory() as session:
            result = await session.execute(
                select(func.count())
                .select_from(Recipe)
                .where(
                    Recipe.category_id == category_id,
                    col(Recipe.is_deleted).is_(False),
                    Recipe.status == RecipeStatus.PUBLISHED,
                )
            )
            return int(result.scalar_one())

    # Uniqueness checks deliberately include soft-deleted rows: the unique constraints do too.
    async def name_taken(self, name: str, *, excluding: uuid.UUID | None = None) -> bool:
        async with self._session_factory() as session:
            query = select(func.count()).select_from(Category).where(Category.name == name)
            if excluding is not None:
                query = query.where(Category.id != excluding)
            return (await session.execute(query)).scalar_one() > 0

    async def slug_taken(self, slug: str) -> bool:
        async with self._session_factory() as session:
            result = await session.execute(select(func.count()).select_from(Category).where(Category.slug == slug))
            return result.scalar_one() > 0

    async def add(self, category: Category) -> None:
        async with self._session_factory() as session:
            session.add(category)
            await self._commit(session)

    async def save(self, category: Category) -> None:
        async with self._session_factory() as session:
            category.updated_at = datetime.now(UTC)
            category.row_version += 1
            await session.merge(category)
            await self._commit(session)

    async def list_recipes(
        self, category_id: uuid.UUID, *, viewer_id: uuid.UUID | None, see_all: bool, page: int, page_size: int
    ) -> tuple[list[Recipe], int]:
        """One page of the category's recipes plus the total. Non-admins see published + their own."""
        conditions = [Recipe.category_id == category_id, col(Recipe.is_deleted).is_(False)]
        if not see_all:
            visible = [Recipe.status == RecipeStatus.PUBLISHED]
            if viewer_id is not None:
                visible.append(Recipe.author_id == viewer_id)
            conditions.append(or_(*visible))
        async with self._session_factory() as session:
            total = (await session.execute(select(func.count()).select_from(Recipe).where(*conditions))).scalar_one()
            result = await session.execute(
                select(Recipe)
                .where(*conditions)
                .order_by(col(Recipe.published_at).desc().nulls_last(), col(Recipe.created_at).desc(), col(Recipe.id))
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            return list(result.scalars().all()), int(total)

    @staticmethod
    async def _commit(session: AsyncSession) -> None:
        try:
            await session.commit()
        except IntegrityError as exc:
            if getattr(exc.orig, "sqlstate", None) != UNIQUE_VIOLATION:
                raise
            raise ConflictError("A category with this name already exists") from exc
