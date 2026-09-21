import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import ColumnElement, func, text, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlmodel import col, or_, select

from culinary_blog.auth.models import User
from culinary_blog.categories.models import Category
from culinary_blog.errors import ConflictError, UnprocessableError
from culinary_blog.recipes.enums import RecipeDifficulty, RecipeStatus
from culinary_blog.recipes.models import Recipe, RecipeImage, RecipeIngredient, RecipeStep

UNIQUE_VIOLATION = "23505"  # PostgreSQL SQLSTATE
FOREIGN_KEY_VIOLATION = "23503"

# Step renumbering parks live rows this far out of the way so the per-row unique check never collides.
_RENUMBER_OFFSET = 1_000_000

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
            try:
                session.add(recipe)
                await session.flush()
                session.add_all([*steps, *ingredients])
                await session.commit()
            except IntegrityError as exc:
                self._raise_domain_error(exc)
                raise

    async def update(self, recipe_id: uuid.UUID, expected_version: int, values: dict[str, object]) -> Recipe | None:
        """Optimistic-concurrency update: one atomic compare-and-swap on `row_version`.

        Returns the updated recipe, or None when no live row matched both the id and `expected_version`
        (someone else changed it first, or it is gone). The check and the write are a single statement, so no
        transaction isolation beyond the default is needed.
        """
        async with self._session_factory() as session:
            try:
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
            except IntegrityError as exc:
                self._raise_domain_error(exc)
                raise
            return recipe

    async def set_status(
        self, recipe_id: uuid.UUID, status: RecipeStatus, *, stamp_published_at: bool
    ) -> Recipe | None:
        """Move a live recipe to `status`, bumping `row_version`; `published_at` is only stamped if still unset."""
        values: dict[str, object] = {"status": status}
        if stamp_published_at:
            values["published_at"] = func.coalesce(col(Recipe.published_at), func.now())
        async with self._session_factory() as session:
            result = await session.execute(
                update(Recipe)
                .where(col(Recipe.id) == recipe_id, col(Recipe.is_deleted).is_(False))
                .values(**values, row_version=col(Recipe.row_version) + 1, updated_at=datetime.now(UTC))
                .returning(Recipe)
            )
            recipe = result.scalar_one_or_none()
            await session.commit()
            return recipe

    async def get_ingredient(self, recipe_id: uuid.UUID, ingredient_id: uuid.UUID) -> RecipeIngredient | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(RecipeIngredient).where(
                    RecipeIngredient.id == ingredient_id,
                    RecipeIngredient.recipe_id == recipe_id,
                    col(RecipeIngredient.is_deleted).is_(False),
                )
            )
            return result.scalars().first()

    async def add_ingredient(self, ingredient: RecipeIngredient, *, append: bool) -> RecipeIngredient:
        """Persist an ingredient; with `append` its `order_index` is set to follow the current last one."""
        async with self._session_factory() as session:
            if append:
                last = await session.execute(
                    select(func.max(RecipeIngredient.order_index)).where(
                        RecipeIngredient.recipe_id == ingredient.recipe_id,
                        col(RecipeIngredient.is_deleted).is_(False),
                    )
                )
                highest = last.scalar_one_or_none()
                ingredient.order_index = 0 if highest is None else highest + 1
            session.add(ingredient)
            await session.commit()
            await session.refresh(ingredient)
            return ingredient

    async def update_ingredient(self, ingredient_id: uuid.UUID, values: dict[str, object]) -> RecipeIngredient | None:
        async with self._session_factory() as session:
            result = await session.execute(
                update(RecipeIngredient)
                .where(col(RecipeIngredient.id) == ingredient_id, col(RecipeIngredient.is_deleted).is_(False))
                .values(**values, row_version=col(RecipeIngredient.row_version) + 1, updated_at=datetime.now(UTC))
                .returning(RecipeIngredient)
            )
            ingredient = result.scalar_one_or_none()
            await session.commit()
            return ingredient

    async def delete_ingredient(self, ingredient_id: uuid.UUID) -> None:
        async with self._session_factory() as session:
            await session.execute(
                update(RecipeIngredient)
                .where(col(RecipeIngredient.id) == ingredient_id)
                .values(
                    is_deleted=True, row_version=col(RecipeIngredient.row_version) + 1, updated_at=datetime.now(UTC)
                )
            )
            await session.commit()

    async def get_step(self, recipe_id: uuid.UUID, step_id: uuid.UUID) -> RecipeStep | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(RecipeStep).where(
                    RecipeStep.id == step_id,
                    RecipeStep.recipe_id == recipe_id,
                    col(RecipeStep.is_deleted).is_(False),
                )
            )
            return result.scalars().first()

    async def add_step(self, step: RecipeStep) -> RecipeStep:
        """Persist a step numbered `max(step_number) + 1`, computed inside the INSERT itself (one statement).

        The recipe row is locked first (held until commit), so concurrent adds and deletes on the same recipe queue up
        and never pick the same number; the unique index on live steps stays as a backstop (409).
        """
        async with self._session_factory() as session:
            try:
                await session.execute(select(Recipe.id).where(Recipe.id == step.recipe_id).with_for_update())
                result = await session.execute(
                    text(
                        "INSERT INTO recipe_steps (id, recipe_id, step_number, title, description, duration_minutes, "
                        "image_url) VALUES (:id, :recipe_id, "
                        "(SELECT COALESCE(MAX(step_number), 0) + 1 FROM recipe_steps "
                        " WHERE recipe_id = :recipe_id AND is_deleted = false), "
                        ":title, :description, :duration_minutes, :image_url) "
                        "RETURNING id, recipe_id, step_number, title, description, duration_minutes, image_url, "
                        "created_at, updated_at, is_deleted, row_version"
                    ),
                    {
                        "id": step.id,
                        "recipe_id": step.recipe_id,
                        "title": step.title,
                        "description": step.description,
                        "duration_minutes": step.duration_minutes,
                        "image_url": step.image_url,
                    },
                )
                saved = RecipeStep(**result.mappings().one())
                await session.commit()
            except IntegrityError as exc:
                if getattr(exc.orig, "sqlstate", None) != UNIQUE_VIOLATION:
                    raise
                raise ConflictError("Another step was added at the same time, please retry") from exc
            return saved

    async def update_step(self, step_id: uuid.UUID, values: dict[str, object]) -> RecipeStep | None:
        async with self._session_factory() as session:
            result = await session.execute(
                update(RecipeStep)
                .where(col(RecipeStep.id) == step_id, col(RecipeStep.is_deleted).is_(False))
                .values(**values, row_version=col(RecipeStep.row_version) + 1, updated_at=datetime.now(UTC))
                .returning(RecipeStep)
            )
            step = result.scalar_one_or_none()
            await session.commit()
            return step

    async def delete_step(self, recipe_id: uuid.UUID, step_id: uuid.UUID) -> None:
        """Soft-delete a step and renumber the survivors to 1..n, in one transaction and a constant 3 statements.

        The unique index on live (recipe_id, step_number) is checked row by row, so a single shift-down UPDATE can
        collide with itself depending on scan order. Hence two set-based passes: park every survivor above the
        offset, then assign 1..n from a window function over the parked order.
        """
        async with self._session_factory() as session:
            # Held until commit: serialises with add_step and other deletes on this recipe (avoids deadlocks).
            await session.execute(select(Recipe.id).where(Recipe.id == recipe_id).with_for_update())
            now = datetime.now(UTC)
            await session.execute(
                update(RecipeStep)
                .where(col(RecipeStep.id) == step_id)
                .values(is_deleted=True, row_version=col(RecipeStep.row_version) + 1, updated_at=now)
            )
            await session.execute(
                text(
                    "UPDATE recipe_steps SET step_number = step_number + :offset "
                    "WHERE recipe_id = :recipe_id AND is_deleted = false"
                ),
                {"offset": _RENUMBER_OFFSET, "recipe_id": recipe_id},
            )
            await session.execute(
                text(
                    "UPDATE recipe_steps AS s "
                    "SET step_number = ranked.position, row_version = s.row_version + 1, updated_at = :now "
                    "FROM (SELECT id, row_number() OVER (ORDER BY step_number) AS position "
                    "      FROM recipe_steps WHERE recipe_id = :recipe_id AND is_deleted = false) AS ranked "
                    "WHERE s.id = ranked.id"
                ),
                {"recipe_id": recipe_id, "now": now},
            )
            await session.commit()

    async def get_image(self, recipe_id: uuid.UUID, image_id: uuid.UUID) -> RecipeImage | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(RecipeImage).where(
                    RecipeImage.id == image_id,
                    RecipeImage.recipe_id == recipe_id,
                    col(RecipeImage.is_deleted).is_(False),
                )
            )
            return result.scalars().first()

    async def add_image(self, image: RecipeImage) -> RecipeImage:
        """Persist an image after the recipe's last one; it becomes primary iff the recipe has no live image yet.

        The recipe row is locked (until commit) so two concurrent first uploads cannot both claim primary.
        """
        async with self._session_factory() as session:
            await session.execute(select(Recipe.id).where(Recipe.id == image.recipe_id).with_for_update())
            live = await session.execute(
                select(func.count(), func.max(RecipeImage.order_index)).where(
                    RecipeImage.recipe_id == image.recipe_id, col(RecipeImage.is_deleted).is_(False)
                )
            )
            count, highest = live.one()
            image.is_primary = count == 0
            image.order_index = 0 if highest is None else highest + 1
            session.add(image)
            await session.commit()
            await session.refresh(image)
            return image

    async def set_primary_image(self, recipe_id: uuid.UUID, image_id: uuid.UUID) -> RecipeImage | None:
        """Make one image primary and every other live image of the recipe non-primary, atomically."""
        async with self._session_factory() as session:
            await session.execute(select(Recipe.id).where(Recipe.id == recipe_id).with_for_update())
            await session.execute(
                update(RecipeImage)
                .where(
                    col(RecipeImage.recipe_id) == recipe_id,
                    col(RecipeImage.is_deleted).is_(False),
                    col(RecipeImage.is_primary) != (col(RecipeImage.id) == image_id),
                )
                .values(
                    is_primary=(col(RecipeImage.id) == image_id),
                    row_version=col(RecipeImage.row_version) + 1,
                    updated_at=datetime.now(UTC),
                )
            )
            result = await session.execute(
                select(RecipeImage).where(RecipeImage.id == image_id, col(RecipeImage.is_deleted).is_(False))
            )
            image = result.scalars().first()
            await session.commit()
            return image

    async def delete_image(self, recipe_id: uuid.UUID, image_id: uuid.UUID) -> RecipeImage | None:
        """Soft-delete an image; if it was primary, promote the first remaining one. Returns the deleted image."""
        async with self._session_factory() as session:
            await session.execute(select(Recipe.id).where(Recipe.id == recipe_id).with_for_update())
            result = await session.execute(
                select(RecipeImage).where(
                    RecipeImage.id == image_id,
                    RecipeImage.recipe_id == recipe_id,
                    col(RecipeImage.is_deleted).is_(False),
                )
            )
            image = result.scalars().first()
            if image is None:
                return None
            now = datetime.now(UTC)
            was_primary = image.is_primary
            image.is_deleted = True
            image.is_primary = False
            image.row_version += 1
            image.updated_at = now
            await session.flush()
            if was_primary:
                first = await session.execute(
                    select(RecipeImage)
                    .where(RecipeImage.recipe_id == recipe_id, col(RecipeImage.is_deleted).is_(False))
                    .order_by(col(RecipeImage.order_index), col(RecipeImage.created_at))
                    .limit(1)
                )
                promoted = first.scalars().first()
                if promoted is not None:
                    promoted.is_primary = True
                    promoted.row_version += 1
                    promoted.updated_at = now
            await session.commit()
            return image

    async def set_image_variants(self, image_id: uuid.UUID, *, medium_url: str, thumbnail_url: str) -> bool:
        """Record the worker-generated variants (FR-JOB-002). False if the image no longer exists."""
        async with self._session_factory() as session:
            result = await session.execute(
                update(RecipeImage)
                .where(col(RecipeImage.id) == image_id, col(RecipeImage.is_deleted).is_(False))
                .values(
                    medium_url=medium_url,
                    thumbnail_url=thumbnail_url,
                    row_version=col(RecipeImage.row_version) + 1,
                    updated_at=datetime.now(UTC),
                )
            )
            await session.commit()
            return result.rowcount > 0  # type: ignore[attr-defined]

    @staticmethod
    def _raise_domain_error(exc: IntegrityError) -> None:
        """Translate the constraint violations callers can cause; anything else is left for the caller to re-raise."""
        sqlstate = getattr(exc.orig, "sqlstate", None)
        # SQLAlchemy's asyncpg adapter wraps the driver error; the constraint name lives on the wrapped exception
        constraint = getattr(getattr(exc.orig, "__cause__", None), "constraint_name", None) or ""
        if sqlstate == UNIQUE_VIOLATION:
            raise ConflictError("A recipe with this slug already exists") from exc
        if sqlstate == FOREIGN_KEY_VIOLATION and "category" in constraint:
            raise UnprocessableError("Category không hợp lệ") from exc

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
