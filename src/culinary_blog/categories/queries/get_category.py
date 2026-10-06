import math
from dataclasses import dataclass

from culinary_blog.auth.principal import Principal
from culinary_blog.cache import keys
from culinary_blog.cache.service import Cache
from culinary_blog.categories.repository import CategoryRepository
from culinary_blog.categories.schemas import CategoryDetailOut, CategoryOut, RecipePage
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
    Only the guest view is cached (one shared entry per page); signed-in viewers always read the database, so a
    draft can never reach the shared cache.
    """

    def __init__(
        self, repository: CategoryRepository, cache: Cache, ttl_seconds: int = keys.RECIPE_TTL_SECONDS
    ) -> None:
        self._repository = repository
        self._cache = cache
        self._ttl_seconds = ttl_seconds

    async def handle(self, query: GetCategoryQuery) -> CategoryDetailOut:
        if query.viewer is not None:
            return await self._load(query)
        return await self._cache.get_or_load_versioned(
            keys.category_detail_namespace(query.slug),
            keys.query_hash(page=query.page, page_size=query.page_size),
            self._ttl_seconds,
            CategoryDetailOut,
            lambda: self._load(query),
        )

    async def _load(self, query: GetCategoryQuery) -> CategoryDetailOut:
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
        # A guest only sees published recipes, so the page total already is the published count.
        is_guest = viewer is None
        recipe_count = total if is_guest else await self._repository.count_published_recipes(category.id)
        return CategoryDetailOut(
            category=CategoryOut(
                **category.model_dump(include=set(CategoryOut.model_fields) - {"recipe_count"}),
                recipe_count=recipe_count,
            ),
            recipes=RecipePage(
                items=recipes,
                total_count=total,
                page=query.page,
                page_size=query.page_size,
                total_pages=math.ceil(total / query.page_size),
            ),
        )
