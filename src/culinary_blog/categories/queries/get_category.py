import math
from dataclasses import dataclass

from culinary_blog.auth.principal import Principal
from culinary_blog.categories.repository import CategoryRepository
from culinary_blog.categories.schemas import CategoryDetailOut, CategoryOut, RecipePage, RecipeSummaryOut
from culinary_blog.cqrs import Query, QueryHandler
from culinary_blog.errors import NotFoundError


@dataclass(frozen=True)
class GetCategoryQuery(Query):
    slug: str
    page: int
    page_size: int
    viewer: Principal | None = None


class GetCategoryHandler(QueryHandler[GetCategoryQuery, CategoryDetailOut]):
    """FR-CAT-002: category by slug plus a page of its recipes.

    Guests see published recipes; a logged-in author also sees their own drafts/archived; Admin sees everything.
    """

    def __init__(self, repository: CategoryRepository) -> None:
        self._repository = repository

    async def handle(self, query: GetCategoryQuery) -> CategoryDetailOut:
        category = await self._repository.get_by_slug(query.slug)
        if category is None:
            raise NotFoundError("Category not found")

        viewer = query.viewer
        recipes, total = await self._repository.list_recipes(
            category.id,
            viewer_id=viewer.user_id if viewer else None,
            see_all=bool(viewer and viewer.is_admin),
            page=query.page,
            page_size=query.page_size,
        )
        recipe_count = await self._repository.count_published_recipes(category.id)
        return CategoryDetailOut(
            category=CategoryOut(
                **category.model_dump(include=set(CategoryOut.model_fields) - {"recipe_count"}),
                recipe_count=recipe_count,
            ),
            recipes=RecipePage(
                items=[RecipeSummaryOut.model_validate(r) for r in recipes],
                total_count=total,
                page=query.page,
                page_size=query.page_size,
                total_pages=math.ceil(total / query.page_size),
            ),
        )
