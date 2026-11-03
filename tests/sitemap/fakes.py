from datetime import datetime

from culinary_blog.categories.repository import CategoryRepository
from culinary_blog.recipes.repository import RecipeRepository

SITE = "https://culinary.example"


class FakeRecipeRepository(RecipeRepository):
    """Published rows only, as the real query filters them. `fail` simulates a database outage."""

    def __init__(self) -> None:  # deliberately skips super().__init__: no database
        self.published: list[tuple[str, datetime]] = []
        self.fail = False

    async def list_published_for_sitemap(self) -> list[tuple[str, datetime]]:
        if self.fail:
            raise RuntimeError("db down")
        return list(self.published)


class FakeCategoryRepository(CategoryRepository):
    def __init__(self) -> None:  # deliberately skips super().__init__: no database
        self.live: list[tuple[str, datetime]] = []

    async def list_for_sitemap(self) -> list[tuple[str, datetime]]:
        return list(self.live)
