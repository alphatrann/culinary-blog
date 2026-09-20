import math
import uuid
from dataclasses import dataclass

from culinary_blog.auth.principal import Principal
from culinary_blog.categories.schemas import RecipeSummaryOut
from culinary_blog.cqrs import Query, QueryHandler
from culinary_blog.recipes.enums import RecipeDifficulty
from culinary_blog.recipes.repository import RecipeRepository
from culinary_blog.recipes.schemas import RecipeListOut


@dataclass(frozen=True)
class ListRecipesQuery(Query):
    page: int
    page_size: int
    sort: str
    category_id: uuid.UUID | None = None
    difficulty: RecipeDifficulty | None = None
    max_cook_time: int | None = None
    viewer: Principal | None = None


class ListRecipesHandler(QueryHandler[ListRecipesQuery, RecipeListOut]):
    """FR-RCP-001: paginated, filtered, sorted recipe list.

    Guests see published recipes; a logged-in author also sees their own draft/archived; Admin sees everything.
    An unknown `category_id` simply yields an empty page.
    """

    def __init__(self, repository: RecipeRepository) -> None:
        self._repository = repository

    async def handle(self, query: ListRecipesQuery) -> RecipeListOut:
        viewer = query.viewer
        recipes, total = await self._repository.list_visible(
            viewer_id=viewer.user_id if viewer else None,
            see_all=bool(viewer and viewer.is_admin),
            category_id=query.category_id,
            difficulty=query.difficulty,
            max_cook_time=query.max_cook_time,
            sort=query.sort,
            page=query.page,
            page_size=query.page_size,
        )
        total_pages = math.ceil(total / query.page_size)
        return RecipeListOut(
            items=[RecipeSummaryOut.model_validate(recipe) for recipe in recipes],
            total_count=total,
            page=query.page,
            page_size=query.page_size,
            total_pages=total_pages,
            has_next_page=query.page < total_pages,
            has_previous_page=query.page > 1,
        )
