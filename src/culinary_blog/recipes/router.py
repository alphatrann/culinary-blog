import uuid
from typing import Annotated

from fastapi import APIRouter, Header, Query, Request, Response

from culinary_blog.auth.dependencies import Authenticator
from culinary_blog.recipes.commands.create_recipe import CreateRecipeCommand, CreateRecipeHandler
from culinary_blog.recipes.commands.update_recipe import UpdateRecipeCommand, UpdateRecipeHandler
from culinary_blog.recipes.enums import RecipeDifficulty
from culinary_blog.recipes.queries.get_recipe import GetRecipeHandler, GetRecipeQuery
from culinary_blog.recipes.queries.list_recipes import ListRecipesHandler, ListRecipesQuery
from culinary_blog.recipes.schemas import (
    DifficultyName,
    IfMatchVersion,
    RecipeCreateRequest,
    RecipeDetailOut,
    RecipeListOut,
    RecipeOut,
    RecipeSort,
    RecipeUpdateRequest,
)


def _etag(row_version: int) -> str:
    return f'"{row_version}"'


class RecipeRouter:
    """HTTP adapter for recipes: authenticates, builds commands/queries, delegates to handlers."""

    def __init__(
        self,
        authenticator: Authenticator,
        create_recipe: CreateRecipeHandler,
        update_recipe: UpdateRecipeHandler,
        list_recipes: ListRecipesHandler,
        get_recipe: GetRecipeHandler,
    ) -> None:
        self._authenticator = authenticator
        self._create_recipe = create_recipe
        self._update_recipe = update_recipe
        self._list_recipes = list_recipes
        self._get_recipe = get_recipe

        self.router = APIRouter(prefix="/api/v1/recipes", tags=["recipes"])
        self.router.add_api_route("", self.list_recipes, methods=["GET"], response_model=RecipeListOut)
        self.router.add_api_route("", self.create, methods=["POST"], response_model=RecipeOut, status_code=201)
        self.router.add_api_route("/{slug}", self.detail, methods=["GET"], response_model=RecipeDetailOut)
        self.router.add_api_route("/{recipe_id}", self.update, methods=["PUT"], response_model=RecipeOut)

    async def list_recipes(
        self,
        request: Request,
        page: Annotated[int, Query(ge=1)] = 1,
        page_size: Annotated[int, Query(ge=1, le=50)] = 12,
        category_id: uuid.UUID | None = None,
        difficulty: DifficultyName | None = None,
        max_cook_time: Annotated[int | None, Query(ge=0)] = None,
        sort: RecipeSort = "-created_at",
    ) -> RecipeListOut:
        viewer = await self._authenticator.optional_principal(request)
        return await self._list_recipes.handle(
            ListRecipesQuery(
                page=page,
                page_size=page_size,
                sort=sort,
                category_id=category_id,
                difficulty=RecipeDifficulty[difficulty.upper()] if difficulty else None,
                max_cook_time=max_cook_time,
                viewer=viewer,
            )
        )

    async def detail(self, slug: str, request: Request, response: Response) -> RecipeDetailOut:
        viewer = await self._authenticator.optional_principal(request)
        recipe = await self._get_recipe.handle(GetRecipeQuery(slug, viewer))
        response.headers["ETag"] = _etag(recipe.row_version)
        return recipe

    async def create(self, body: RecipeCreateRequest, request: Request, response: Response) -> RecipeOut:
        actor = await self._authenticator.require_principal(request)
        recipe = await self._create_recipe.handle(
            CreateRecipeCommand(
                actor=actor,
                title=body.title,
                description=body.description,
                category_id=body.category_id,
                prep_time_minutes=body.prep_time_minutes,
                cook_time_minutes=body.cook_time_minutes,
                servings=body.servings,
                difficulty=body.difficulty,
                nutrition=body.nutrition,
                steps=body.steps,
                ingredients=body.ingredients,
            )
        )
        response.headers["Location"] = f"/api/v1/recipes/{recipe.slug}"
        response.headers["ETag"] = _etag(recipe.row_version)
        return recipe

    async def update(
        self,
        recipe_id: uuid.UUID,
        body: RecipeUpdateRequest,
        request: Request,
        response: Response,
        if_match: Annotated[IfMatchVersion, Header(alias="If-Match")],
    ) -> RecipeOut:
        actor = await self._authenticator.require_principal(request)
        recipe = await self._update_recipe.handle(
            UpdateRecipeCommand(
                actor=actor,
                recipe_id=recipe_id,
                expected_version=if_match,
                title=body.title,
                description=body.description,
                category_id=body.category_id,
                prep_time_minutes=body.prep_time_minutes,
                cook_time_minutes=body.cook_time_minutes,
                servings=body.servings,
                difficulty=body.difficulty,
                nutrition=body.nutrition,
            )
        )
        response.headers["ETag"] = _etag(recipe.row_version)
        return recipe
