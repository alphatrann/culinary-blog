import uuid
from datetime import UTC, datetime

from culinary_blog.auth.models import User
from culinary_blog.auth.principal import Principal
from culinary_blog.categories.models import Category
from culinary_blog.errors import ConflictError, UnprocessableError
from culinary_blog.recipes.enums import RecipeDifficulty, RecipeStatus
from culinary_blog.recipes.models import Recipe, RecipeImage, RecipeIngredient, RecipeStep
from culinary_blog.recipes.repository import RecipeAggregate, RecipeRepository

ADMIN = Principal(uuid.uuid4(), ("admin",))
AUTHOR = Principal(uuid.uuid4(), ("author",))
OTHER_AUTHOR = Principal(uuid.uuid4(), ("author",))
READER = Principal(uuid.uuid4(), ("reader",))
NO_ROLES = Principal(uuid.uuid4(), ())


class FakeRecipeRepository(RecipeRepository):
    """In-memory stand-in mirroring the real repository (slug uniqueness includes soft-deleted rows)."""

    def __init__(self) -> None:  # deliberately skips super().__init__: no database
        self.categories: dict[uuid.UUID, Category] = {}
        self.users: dict[uuid.UUID, User] = {}
        self.recipes: dict[uuid.UUID, Recipe] = {}
        self.steps: list[RecipeStep] = []
        self.ingredients: list[RecipeIngredient] = []
        self.images: list[RecipeImage] = []

    def add_category(self, name: str | None = None) -> uuid.UUID:
        name = name or f"Category {len(self.categories) + 1}"
        category = Category(name=name, slug=name.lower().replace(" ", "-"))
        self.categories[category.id] = category
        return category.id

    def add_user(self, principal: Principal, display_name: str = "Chef") -> User:
        user = User(
            id=principal.user_id,
            email=f"{principal.user_id}@example.com",
            display_name=display_name,
            roles=list(principal.roles),
        )
        self.users[user.id] = user
        return user

    def seed_recipe(
        self,
        author: Principal,
        status: RecipeStatus = RecipeStatus.PUBLISHED,
        category_id: uuid.UUID | None = None,
        title: str = "Pho Bo",
        **overrides: object,
    ) -> Recipe:
        """Insert a recipe directly (bypassing the create handler), with its author registered."""
        if author.user_id not in self.users:
            self.add_user(author)
        fields: dict[str, object] = {
            "title": title,
            "slug": f"{title.lower().replace(' ', '-')}-{uuid.uuid4().hex[:6]}",
            "description": "desc",
            "prep_time_minutes": 10,
            "cook_time_minutes": 20,
            "servings": 2,
            "status": status,
            "category_id": category_id or self.add_category(),
            "author_id": author.user_id,
            "published_at": datetime.now(UTC) if status == RecipeStatus.PUBLISHED else None,
        } | overrides
        recipe = Recipe(**fields)  # type: ignore[arg-type]
        self.recipes[recipe.id] = recipe
        return recipe

    def _live(self) -> list[Recipe]:
        return [r for r in self.recipes.values() if not r.is_deleted]

    def _check_category_fk(self, category_id: uuid.UUID) -> None:
        """Stand-in for the FK constraint the real repository translates into a 422."""
        if category_id not in self.categories:
            raise UnprocessableError("Category không hợp lệ")

    async def slug_taken(self, slug: str) -> bool:
        return any(r.slug == slug for r in self.recipes.values())

    async def get_by_id(self, recipe_id: uuid.UUID) -> Recipe | None:
        return next((r for r in self._live() if r.id == recipe_id), None)

    async def get_children(self, recipe_id: uuid.UUID) -> tuple[list[RecipeStep], list[RecipeIngredient]]:
        steps = sorted(
            (s for s in self.steps if s.recipe_id == recipe_id and not s.is_deleted), key=lambda s: s.step_number
        )
        ingredients = sorted(
            (i for i in self.ingredients if i.recipe_id == recipe_id and not i.is_deleted), key=lambda i: i.order_index
        )
        return steps, ingredients

    async def get_aggregate_by_slug(self, slug: str) -> RecipeAggregate | None:
        recipe = next((r for r in self._live() if r.slug == slug), None)
        if recipe is None:
            return None
        steps, ingredients = await self.get_children(recipe.id)
        images = sorted(
            (i for i in self.images if i.recipe_id == recipe.id and not i.is_deleted), key=lambda i: i.order_index
        )
        return RecipeAggregate(
            recipe, self.categories[recipe.category_id], self.users[recipe.author_id], steps, ingredients, images
        )

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
        visible = [
            r
            for r in self._live()
            if (see_all or r.status == RecipeStatus.PUBLISHED or (viewer_id is not None and r.author_id == viewer_id))
            and (category_id is None or r.category_id == category_id)
            and (difficulty is None or r.difficulty == difficulty)
            and (max_cook_time is None or r.cook_time_minutes <= max_cook_time)
        ]
        visible.sort(key=lambda r: getattr(r, sort.removeprefix("-")), reverse=sort.startswith("-"))
        start = (page - 1) * page_size
        return visible[start : start + page_size], len(visible)

    async def add(self, recipe: Recipe, steps: list[RecipeStep], ingredients: list[RecipeIngredient]) -> None:
        self._check_category_fk(recipe.category_id)
        if any(r.slug == recipe.slug for r in self.recipes.values()):  # the unique constraint
            raise ConflictError("A recipe with this slug already exists")
        self.recipes[recipe.id] = recipe
        self.steps.extend(steps)
        self.ingredients.extend(ingredients)

    async def update(self, recipe_id: uuid.UUID, expected_version: int, values: dict[str, object]) -> Recipe | None:
        recipe = await self.get_by_id(recipe_id)
        if recipe is None or recipe.row_version != expected_version:
            return None
        if "category_id" in values:
            self._check_category_fk(values["category_id"])  # type: ignore[arg-type]
        for name, value in values.items():
            setattr(recipe, name, value)
        recipe.row_version += 1
        recipe.updated_at = datetime.now(UTC)
        return recipe

    async def set_status(
        self, recipe_id: uuid.UUID, status: RecipeStatus, *, stamp_published_at: bool
    ) -> Recipe | None:
        recipe = await self.get_by_id(recipe_id)
        if recipe is None:
            return None
        recipe.status = status
        if stamp_published_at and recipe.published_at is None:
            recipe.published_at = datetime.now(UTC)
        recipe.row_version += 1
        recipe.updated_at = datetime.now(UTC)
        return recipe

    async def get_ingredient(self, recipe_id: uuid.UUID, ingredient_id: uuid.UUID) -> RecipeIngredient | None:
        return next(
            (i for i in self.ingredients if i.id == ingredient_id and i.recipe_id == recipe_id and not i.is_deleted),
            None,
        )

    async def add_ingredient(self, ingredient: RecipeIngredient, *, append: bool) -> RecipeIngredient:
        if append:
            live = [i.order_index for i in self.ingredients if i.recipe_id == ingredient.recipe_id and not i.is_deleted]
            ingredient.order_index = max(live, default=-1) + 1
        self.ingredients.append(ingredient)
        return ingredient

    async def update_ingredient(self, ingredient_id: uuid.UUID, values: dict[str, object]) -> RecipeIngredient | None:
        ingredient = next((i for i in self.ingredients if i.id == ingredient_id and not i.is_deleted), None)
        if ingredient is None:
            return None
        for name, value in values.items():
            setattr(ingredient, name, value)
        return ingredient

    async def delete_ingredient(self, ingredient_id: uuid.UUID) -> None:
        for ingredient in self.ingredients:
            if ingredient.id == ingredient_id:
                ingredient.is_deleted = True

    async def get_step(self, recipe_id: uuid.UUID, step_id: uuid.UUID) -> RecipeStep | None:
        return next((s for s in self.steps if s.id == step_id and s.recipe_id == recipe_id and not s.is_deleted), None)

    async def add_step(self, step: RecipeStep) -> RecipeStep:
        live = [s.step_number for s in self.steps if s.recipe_id == step.recipe_id and not s.is_deleted]
        step.step_number = max(live, default=0) + 1
        self.steps.append(step)
        return step

    async def update_step(self, step_id: uuid.UUID, values: dict[str, object]) -> RecipeStep | None:
        step = next((s for s in self.steps if s.id == step_id and not s.is_deleted), None)
        if step is None:
            return None
        for name, value in values.items():
            setattr(step, name, value)
        return step

    async def delete_step(self, recipe_id: uuid.UUID, step_id: uuid.UUID) -> None:
        for step in self.steps:
            if step.id == step_id:
                step.is_deleted = True
        survivors = sorted(
            (s for s in self.steps if s.recipe_id == recipe_id and not s.is_deleted), key=lambda s: s.step_number
        )
        for position, step in enumerate(survivors, start=1):
            step.step_number = position
