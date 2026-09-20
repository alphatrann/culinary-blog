import uuid
from typing import Annotated

from fastapi import APIRouter, Query, Request, Response

from culinary_blog.auth.dependencies import Authenticator
from culinary_blog.categories.commands.create_category import CreateCategoryCommand, CreateCategoryHandler
from culinary_blog.categories.commands.update_category import UpdateCategoryCommand, UpdateCategoryHandler
from culinary_blog.categories.queries.get_category import GetCategoryHandler, GetCategoryQuery
from culinary_blog.categories.queries.list_categories import ListCategoriesHandler, ListCategoriesQuery
from culinary_blog.categories.schemas import (
    CategoryCreateRequest,
    CategoryDetailOut,
    CategoryOut,
    CategoryUpdateRequest,
)


class CategoryRouter:
    """HTTP adapter for categories: authenticates, builds commands/queries, delegates to handlers."""

    def __init__(
        self,
        authenticator: Authenticator,
        create_category: CreateCategoryHandler,
        update_category: UpdateCategoryHandler,
        list_categories: ListCategoriesHandler,
        get_category: GetCategoryHandler,
    ) -> None:
        self._authenticator = authenticator
        self._create_category = create_category
        self._update_category = update_category
        self._list_categories = list_categories
        self._get_category = get_category

        self.router = APIRouter(prefix="/api/v1/categories", tags=["categories"])
        self.router.add_api_route("", self.list_categories, methods=["GET"], response_model=list[CategoryOut])
        self.router.add_api_route("", self.create, methods=["POST"], response_model=CategoryOut, status_code=201)
        self.router.add_api_route("/{slug}", self.detail, methods=["GET"], response_model=CategoryDetailOut)
        self.router.add_api_route("/{category_id}", self.update, methods=["PUT"], response_model=CategoryOut)

    async def list_categories(self) -> list[CategoryOut]:
        return await self._list_categories.handle(ListCategoriesQuery())

    async def detail(
        self,
        slug: str,
        request: Request,
        page: Annotated[int, Query(ge=1)] = 1,
        page_size: Annotated[int, Query(ge=1, le=50)] = 12,
    ) -> CategoryDetailOut:
        viewer = await self._authenticator.optional_principal(request)
        return await self._get_category.handle(GetCategoryQuery(slug, page, page_size, viewer))

    async def create(self, body: CategoryCreateRequest, request: Request, response: Response) -> CategoryOut:
        actor = await self._authenticator.require_principal(request)
        category = await self._create_category.handle(
            CreateCategoryCommand(actor, body.name, body.description, body.image_url)
        )
        response.headers["Location"] = f"/api/v1/categories/{category.slug}"
        return category

    async def update(self, category_id: uuid.UUID, body: CategoryUpdateRequest, request: Request) -> CategoryOut:
        actor = await self._authenticator.require_principal(request)
        return await self._update_category.handle(
            UpdateCategoryCommand(actor, category_id, body.name, body.description, body.image_url, body.order_index)
        )
