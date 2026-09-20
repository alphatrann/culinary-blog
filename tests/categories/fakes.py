import uuid
from datetime import UTC, datetime

from culinary_blog.auth.principal import Principal
from culinary_blog.categories.models import Category
from culinary_blog.categories.repository import CategoryRepository
from culinary_blog.errors import ConflictError
from culinary_blog.recipes.enums import RecipeStatus
from culinary_blog.recipes.models import Recipe

ADMIN = Principal(uuid.uuid4(), ("admin",))
AUTHOR = Principal(uuid.uuid4(), ("author",))
OTHER_AUTHOR = Principal(uuid.uuid4(), ("author",))


class FakeCategoryRepository(CategoryRepository):
    """In-memory stand-in mirroring the real repository (uniqueness includes soft-deleted rows)."""

    def __init__(self) -> None:  # deliberately skips super().__init__: no database
        self.categories: dict[uuid.UUID, Category] = {}
        self.recipes: list[Recipe] = []

    def add_recipe(
        self, category: Category, author: Principal, status: RecipeStatus, title: str = "Pho", **overrides: object
    ) -> Recipe:
        recipe = Recipe(
            title=title,
            slug=f"{title.lower()}-{uuid.uuid4().hex[:6]}",
            description="desc",
            prep_time_minutes=10,
            cook_time_minutes=20,
            servings=2,
            status=status,
            category_id=category.id,
            author_id=author.user_id,
            published_at=datetime.now(UTC) if status == RecipeStatus.PUBLISHED else None,
            **overrides,  # type: ignore[arg-type]
        )
        self.recipes.append(recipe)
        return recipe

    def _live(self) -> list[Category]:
        return [c for c in self.categories.values() if not c.is_deleted]

    def _published(self, category_id: uuid.UUID) -> int:
        return sum(
            1
            for r in self.recipes
            if r.category_id == category_id and r.status == RecipeStatus.PUBLISHED and not r.is_deleted
        )

    async def list_with_recipe_counts(self) -> list[tuple[Category, int]]:
        return [(c, self._published(c.id)) for c in sorted(self._live(), key=lambda c: c.name)]

    async def get_by_slug(self, slug: str) -> Category | None:
        return next((c for c in self._live() if c.slug == slug), None)

    async def get_by_id(self, category_id: uuid.UUID) -> Category | None:
        return next((c for c in self._live() if c.id == category_id), None)

    async def count_published_recipes(self, category_id: uuid.UUID) -> int:
        return self._published(category_id)

    async def name_taken(self, name: str, *, excluding: uuid.UUID | None = None) -> bool:
        return any(c.name == name and c.id != excluding for c in self.categories.values())

    async def slug_taken(self, slug: str) -> bool:
        return any(c.slug == slug for c in self.categories.values())

    async def add(self, category: Category) -> None:
        if await self.name_taken(category.name) or await self.slug_taken(category.slug):
            raise ConflictError("A category with this name already exists")
        self.categories[category.id] = category

    async def save(self, category: Category) -> None:
        category.row_version += 1
        self.categories[category.id] = category

    async def list_recipes(
        self, category_id: uuid.UUID, *, viewer_id: uuid.UUID | None, see_all: bool, page: int, page_size: int
    ) -> tuple[list[Recipe], int]:
        visible = [
            r
            for r in self.recipes
            if r.category_id == category_id
            and not r.is_deleted
            and (see_all or r.status == RecipeStatus.PUBLISHED or (viewer_id is not None and r.author_id == viewer_id))
        ]
        start = (page - 1) * page_size
        return visible[start : start + page_size], len(visible)


def make_category(repository: FakeCategoryRepository, name: str = "Main", slug: str = "main", **kw: object) -> Category:
    category = Category(name=name, slug=slug, **kw)  # type: ignore[arg-type]
    repository.categories[category.id] = category
    return category
