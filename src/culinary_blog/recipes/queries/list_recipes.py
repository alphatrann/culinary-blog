import math
import uuid
from dataclasses import dataclass

from culinary_blog.auth.principal import Principal
from culinary_blog.cache import keys
from culinary_blog.cache.service import Cache
from culinary_blog.cqrs import Query, QueryHandler
from culinary_blog.errors import ForbiddenError, UnauthorizedError
from culinary_blog.recipes.enums import RecipeDifficulty, RecipeStatus
from culinary_blog.recipes.repository import RecipeRepository
from culinary_blog.recipes.schemas import RecipeListOut, RecipeStatusCounts


@dataclass(frozen=True)
class ListRecipesQuery(Query):
    page: int
    page_size: int
    sort: str
    category_id: uuid.UUID | None = None
    difficulty: RecipeDifficulty | None = None
    max_cook_time: int | None = None
    viewer: Principal | None = None
    # Owner filter ("my recipes"). Only the owner or an Admin may set it; the router resolves `me` first.
    author_id: uuid.UUID | None = None
    status: RecipeStatus | None = None


class ListRecipesHandler(QueryHandler[ListRecipesQuery, RecipeListOut]):
    """FR-RCP-001: paginated, filtered, sorted recipe list.

    Guests see published recipes; a logged-in author also sees their own draft/archived; Admin sees everything.
    An unknown `category_id` simply yields an empty page. Only the guest view is cached (keyed by the full query);
    signed-in viewers see a different, per-user set and always read the database.

    An `author_id` filter lists one author's recipes and includes per-status counts. It is for that author or an Admin.
    """

    def __init__(self, repository: RecipeRepository, cache: Cache, ttl_seconds: int = keys.RECIPE_TTL_SECONDS) -> None:
        self._repository = repository
        self._cache = cache
        self._ttl_seconds = ttl_seconds

    async def handle(self, query: ListRecipesQuery) -> RecipeListOut:
        if query.author_id is not None:
            _ensure_can_list_author(query)
        if query.viewer is not None:
            return await self._load(query)
        return await self._cache.get_or_load_versioned(
            keys.NS_RECIPE_LIST,
            keys.query_hash(
                page=query.page,
                page_size=query.page_size,
                sort=query.sort,
                category_id=query.category_id,
                difficulty=query.difficulty,
                max_cook_time=query.max_cook_time,
                status=query.status,
            ),
            self._ttl_seconds,
            RecipeListOut,
            lambda: self._load(query),
        )

    async def _load(self, query: ListRecipesQuery) -> RecipeListOut:
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
            author_id=query.author_id,
            status=query.status,
        )
        total_pages = math.ceil(total / query.page_size)
        counts = None
        if query.author_id is not None:
            by_status = await self._repository.count_by_status(query.author_id)
            counts = RecipeStatusCounts(
                draft=by_status.get(RecipeStatus.DRAFT, 0),
                published=by_status.get(RecipeStatus.PUBLISHED, 0),
                archived=by_status.get(RecipeStatus.ARCHIVED, 0),
            )
        return RecipeListOut(
            items=recipes,
            total_count=total,
            page=query.page,
            page_size=query.page_size,
            total_pages=total_pages,
            has_next_page=query.page < total_pages,
            has_previous_page=query.page > 1,
            status_counts=counts,
        )


def _ensure_can_list_author(query: ListRecipesQuery) -> None:
    viewer = query.viewer
    if viewer is None:
        raise UnauthorizedError("Cần đăng nhập để xem công thức của tác giả.")
    if not (viewer.is_admin or viewer.user_id == query.author_id):
        raise ForbiddenError("Chỉ tác giả hoặc quản trị viên mới xem được danh sách này.")
