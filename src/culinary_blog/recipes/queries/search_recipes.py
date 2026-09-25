import math
import uuid
from dataclasses import dataclass

from culinary_blog.categories.schemas import RecipeSummaryOut
from culinary_blog.cqrs import Query, QueryHandler
from culinary_blog.recipes.enums import RecipeDifficulty
from culinary_blog.recipes.repository import RecipeRepository
from culinary_blog.recipes.schemas import RecipeSearchResultOut, RecipeSearchResultsOut


@dataclass(frozen=True)
class SearchRecipesQuery(Query):
    q: str
    page: int
    page_size: int
    category_id: uuid.UUID | None = None
    difficulty: RecipeDifficulty | None = None
    max_cook_time: int | None = None


class SearchRecipesHandler(QueryHandler[SearchRecipesQuery, RecipeSearchResultsOut]):
    """FR-SRCH-001: diacritic-insensitive, typo-tolerant search over recipe titles.

    Published recipes only, regardless of who is asking — search has no author-owned-drafts carve-out.
    """

    def __init__(self, repository: RecipeRepository) -> None:
        self._repository = repository

    async def handle(self, query: SearchRecipesQuery) -> RecipeSearchResultsOut:
        results, total = await self._repository.search_published(
            query=query.q,
            category_id=query.category_id,
            difficulty=query.difficulty,
            max_cook_time=query.max_cook_time,
            page=query.page,
            page_size=query.page_size,
        )
        total_pages = math.ceil(total / query.page_size)
        return RecipeSearchResultsOut(
            items=[
                RecipeSearchResultOut(**RecipeSummaryOut.model_validate(recipe).model_dump(), relevance_score=relevance)
                for recipe, relevance in results
            ],
            total_count=total,
            page=query.page,
            page_size=query.page_size,
            total_pages=total_pages,
            has_next_page=query.page < total_pages,
            has_previous_page=query.page > 1,
        )
