from dataclasses import dataclass

from culinary_blog.categories.repository import CategoryRepository
from culinary_blog.categories.schemas import CategoryOut
from culinary_blog.cqrs import Query, QueryHandler


@dataclass(frozen=True)
class ListCategoriesQuery(Query):
    pass


class ListCategoriesHandler(QueryHandler[ListCategoriesQuery, list[CategoryOut]]):
    """FR-CAT-001: public list of every category with its published-recipe count. Direct DB read until M6b."""

    def __init__(self, repository: CategoryRepository) -> None:
        self._repository = repository

    async def handle(self, query: ListCategoriesQuery) -> list[CategoryOut]:
        rows = await self._repository.list_with_recipe_counts()
        return [
            CategoryOut(**c.model_dump(include=set(CategoryOut.model_fields) - {"recipe_count"}), recipe_count=count)
            for c, count in rows
        ]
