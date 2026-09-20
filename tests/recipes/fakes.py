import uuid

from culinary_blog.auth.principal import Principal
from culinary_blog.errors import ConflictError
from culinary_blog.recipes.models import Recipe, RecipeIngredient, RecipeStep
from culinary_blog.recipes.repository import RecipeRepository

ADMIN = Principal(uuid.uuid4(), ("admin",))
AUTHOR = Principal(uuid.uuid4(), ("author",))
READER = Principal(uuid.uuid4(), ("reader",))
NO_ROLES = Principal(uuid.uuid4(), ())


class FakeRecipeRepository(RecipeRepository):
    """In-memory stand-in mirroring the real repository (slug uniqueness includes soft-deleted rows)."""

    def __init__(self) -> None:  # deliberately skips super().__init__: no database
        self.category_ids: set[uuid.UUID] = set()
        self.recipes: dict[uuid.UUID, Recipe] = {}
        self.steps: list[RecipeStep] = []
        self.ingredients: list[RecipeIngredient] = []

    def add_category(self) -> uuid.UUID:
        category_id = uuid.uuid4()
        self.category_ids.add(category_id)
        return category_id

    async def category_exists(self, category_id: uuid.UUID) -> bool:
        return category_id in self.category_ids

    async def slug_taken(self, slug: str) -> bool:
        return any(r.slug == slug for r in self.recipes.values())

    async def add(self, recipe: Recipe, steps: list[RecipeStep], ingredients: list[RecipeIngredient]) -> None:
        if any(r.slug == recipe.slug for r in self.recipes.values()):  # the unique constraint
            raise ConflictError("A recipe with this slug already exists")
        self.recipes[recipe.id] = recipe
        self.steps.extend(steps)
        self.ingredients.extend(ingredients)
