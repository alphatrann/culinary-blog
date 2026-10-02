from dataclasses import dataclass

from culinary_blog.cache import keys
from culinary_blog.cache.service import Cache
from culinary_blog.categories.repository import CategoryRepository
from culinary_blog.categories.schemas import CategoryListOut, CategoryOut
from culinary_blog.cqrs import Query, QueryHandler


@dataclass(frozen=True)
class ListCategoriesQuery(Query):
    pass


class ListCategoriesHandler(QueryHandler[ListCategoriesQuery, list[CategoryOut]]):
    """FR-CAT-001: public list of every category with its published-recipe count, cached as one entry (ADR-0003)."""

    def __init__(
        self, repository: CategoryRepository, cache: Cache, ttl_seconds: int = keys.CATEGORY_TTL_SECONDS
    ) -> None:
        self._repository = repository
        self._cache = cache
        self._ttl_seconds = ttl_seconds

    async def handle(self, query: ListCategoriesQuery) -> list[CategoryOut]:
        cached = await self._cache.get_or_load(keys.CATEGORIES_ALL, self._ttl_seconds, CategoryListOut, self._load)
        return cached.items

    async def _load(self) -> CategoryListOut:
        rows = await self._repository.list_with_recipe_counts()
        return CategoryListOut(
            items=[
                CategoryOut(
                    **c.model_dump(include=set(CategoryOut.model_fields) - {"recipe_count"}), recipe_count=count
                )
                for c, count in rows
            ]
        )
