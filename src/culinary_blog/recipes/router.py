import uuid
from typing import Annotated

from fastapi import APIRouter, File, Form, Header, Query, Request, Response, UploadFile

from culinary_blog.auth.dependencies import Authenticator
from culinary_blog.recipes.commands.add_ingredient import AddIngredientCommand, AddIngredientHandler
from culinary_blog.recipes.commands.add_step import AddStepCommand, AddStepHandler
from culinary_blog.recipes.commands.create_recipe import CreateRecipeCommand, CreateRecipeHandler
from culinary_blog.recipes.commands.delete_image import DeleteImageCommand, DeleteImageHandler
from culinary_blog.recipes.commands.delete_ingredient import DeleteIngredientCommand, DeleteIngredientHandler
from culinary_blog.recipes.commands.delete_recipe import DeleteRecipeCommand, DeleteRecipeHandler
from culinary_blog.recipes.commands.delete_step import DeleteStepCommand, DeleteStepHandler
from culinary_blog.recipes.commands.publish_recipe import PublishRecipeCommand, PublishRecipeHandler
from culinary_blog.recipes.commands.set_primary_image import SetPrimaryImageCommand, SetPrimaryImageHandler
from culinary_blog.recipes.commands.unpublish_recipe import UnpublishRecipeCommand, UnpublishRecipeHandler
from culinary_blog.recipes.commands.update_ingredient import UpdateIngredientCommand, UpdateIngredientHandler
from culinary_blog.recipes.commands.update_recipe import UpdateRecipeCommand, UpdateRecipeHandler
from culinary_blog.recipes.commands.update_step import UpdateStepCommand, UpdateStepHandler
from culinary_blog.recipes.commands.upload_image import UploadImageCommand, UploadImageHandler
from culinary_blog.recipes.enums import RecipeDifficulty
from culinary_blog.recipes.queries.get_recipe import GetRecipeHandler, GetRecipeQuery
from culinary_blog.recipes.queries.list_recipes import ListRecipesHandler, ListRecipesQuery
from culinary_blog.recipes.queries.search_recipes import SearchRecipesHandler, SearchRecipesQuery
from culinary_blog.recipes.schemas import (
    DifficultyName,
    IfMatchVersion,
    IngredientIn,
    IngredientOut,
    RecipeCreateRequest,
    RecipeDetailOut,
    RecipeImageOut,
    RecipeListOut,
    RecipeOut,
    RecipeSearchResultsOut,
    RecipeSort,
    RecipeUpdateRequest,
    StepIn,
    StepOut,
)
from culinary_blog.storage.images import MAX_IMAGE_BYTES, validate_image


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
        search_recipes: SearchRecipesHandler,
        get_recipe: GetRecipeHandler,
        publish_recipe: PublishRecipeHandler,
        unpublish_recipe: UnpublishRecipeHandler,
        add_ingredient: AddIngredientHandler,
        update_ingredient: UpdateIngredientHandler,
        delete_ingredient: DeleteIngredientHandler,
        add_step: AddStepHandler,
        update_step: UpdateStepHandler,
        delete_step: DeleteStepHandler,
        upload_image: UploadImageHandler,
        set_primary_image: SetPrimaryImageHandler,
        delete_image: DeleteImageHandler,
        delete_recipe: DeleteRecipeHandler,
    ) -> None:
        self._authenticator = authenticator
        self._create_recipe = create_recipe
        self._update_recipe = update_recipe
        self._list_recipes = list_recipes
        self._search_recipes = search_recipes
        self._get_recipe = get_recipe
        self._publish_recipe = publish_recipe
        self._delete_recipe = delete_recipe
        self._unpublish_recipe = unpublish_recipe
        self._add_ingredient = add_ingredient
        self._update_ingredient = update_ingredient
        self._delete_ingredient = delete_ingredient
        self._add_step = add_step
        self._update_step = update_step
        self._delete_step = delete_step
        self._upload_image = upload_image
        self._set_primary_image = set_primary_image
        self._delete_image = delete_image

        self.router = APIRouter(prefix="/api/v1/recipes", tags=["recipes"])
        self.router.add_api_route("", self.list_recipes, methods=["GET"], response_model=RecipeListOut)
        self.router.add_api_route("", self.create, methods=["POST"], response_model=RecipeOut, status_code=201)
        # Registered before "/{slug}": otherwise "/search" would be swallowed by the slug path parameter.
        self.router.add_api_route("/search", self.search, methods=["GET"], response_model=RecipeSearchResultsOut)
        self.router.add_api_route("/{slug}", self.detail, methods=["GET"], response_model=RecipeDetailOut)
        self.router.add_api_route("/{recipe_id}", self.update, methods=["PUT"], response_model=RecipeOut)
        self.router.add_api_route("/{recipe_id}", self.delete, methods=["DELETE"], status_code=204)
        self.router.add_api_route("/{recipe_id}/publish", self.publish, methods=["PATCH"], response_model=RecipeOut)
        self.router.add_api_route("/{recipe_id}/unpublish", self.unpublish, methods=["PATCH"], response_model=RecipeOut)
        self.router.add_api_route(
            "/{recipe_id}/ingredients",
            self.add_ingredient,
            methods=["POST"],
            response_model=IngredientOut,
            status_code=201,
        )
        self.router.add_api_route(
            "/{recipe_id}/ingredients/{ingredient_id}",
            self.update_ingredient,
            methods=["PUT"],
            response_model=IngredientOut,
        )
        self.router.add_api_route(
            "/{recipe_id}/ingredients/{ingredient_id}", self.delete_ingredient, methods=["DELETE"], status_code=204
        )
        self.router.add_api_route(
            "/{recipe_id}/steps", self.add_step, methods=["POST"], response_model=StepOut, status_code=201
        )
        self.router.add_api_route(
            "/{recipe_id}/steps/{step_id}", self.update_step, methods=["PUT"], response_model=StepOut
        )
        self.router.add_api_route("/{recipe_id}/steps/{step_id}", self.delete_step, methods=["DELETE"], status_code=204)
        self.router.add_api_route(
            "/{recipe_id}/images", self.upload_image, methods=["POST"], response_model=RecipeImageOut, status_code=201
        )
        self.router.add_api_route(
            "/{recipe_id}/images/{image_id}/primary",
            self.set_primary_image,
            methods=["PATCH"],
            response_model=RecipeImageOut,
        )
        self.router.add_api_route(
            "/{recipe_id}/images/{image_id}", self.delete_image, methods=["DELETE"], status_code=204
        )

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

    async def search(
        self,
        q: Annotated[str, Query(min_length=2, max_length=200)],
        page: Annotated[int, Query(ge=1)] = 1,
        page_size: Annotated[int, Query(ge=1, le=50)] = 12,
        category_id: uuid.UUID | None = None,
        difficulty: DifficultyName | None = None,
        max_cook_time: Annotated[int | None, Query(ge=0)] = None,
    ) -> RecipeSearchResultsOut:
        return await self._search_recipes.handle(
            SearchRecipesQuery(
                q=q,
                page=page,
                page_size=page_size,
                category_id=category_id,
                difficulty=RecipeDifficulty[difficulty.upper()] if difficulty else None,
                max_cook_time=max_cook_time,
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

    async def delete(self, recipe_id: uuid.UUID, request: Request) -> Response:
        actor = await self._authenticator.require_principal(request)
        await self._delete_recipe.handle(DeleteRecipeCommand(actor=actor, recipe_id=recipe_id))
        return Response(status_code=204)

    async def publish(self, recipe_id: uuid.UUID, request: Request, response: Response) -> RecipeOut:
        actor = await self._authenticator.require_principal(request)
        recipe = await self._publish_recipe.handle(PublishRecipeCommand(actor, recipe_id))
        response.headers["ETag"] = _etag(recipe.row_version)
        return recipe

    async def unpublish(self, recipe_id: uuid.UUID, request: Request, response: Response) -> RecipeOut:
        actor = await self._authenticator.require_principal(request)
        recipe = await self._unpublish_recipe.handle(UnpublishRecipeCommand(actor, recipe_id))
        response.headers["ETag"] = _etag(recipe.row_version)
        return recipe

    async def add_ingredient(self, recipe_id: uuid.UUID, body: IngredientIn, request: Request) -> IngredientOut:
        actor = await self._authenticator.require_principal(request)
        return await self._add_ingredient.handle(AddIngredientCommand(actor, recipe_id, body))

    async def update_ingredient(
        self, recipe_id: uuid.UUID, ingredient_id: uuid.UUID, body: IngredientIn, request: Request
    ) -> IngredientOut:
        actor = await self._authenticator.require_principal(request)
        return await self._update_ingredient.handle(UpdateIngredientCommand(actor, recipe_id, ingredient_id, body))

    async def delete_ingredient(self, recipe_id: uuid.UUID, ingredient_id: uuid.UUID, request: Request) -> Response:
        actor = await self._authenticator.require_principal(request)
        await self._delete_ingredient.handle(DeleteIngredientCommand(actor, recipe_id, ingredient_id))
        return Response(status_code=204)

    async def add_step(self, recipe_id: uuid.UUID, body: StepIn, request: Request) -> StepOut:
        actor = await self._authenticator.require_principal(request)
        return await self._add_step.handle(AddStepCommand(actor, recipe_id, body))

    async def update_step(self, recipe_id: uuid.UUID, step_id: uuid.UUID, body: StepIn, request: Request) -> StepOut:
        actor = await self._authenticator.require_principal(request)
        return await self._update_step.handle(UpdateStepCommand(actor, recipe_id, step_id, body))

    async def delete_step(self, recipe_id: uuid.UUID, step_id: uuid.UUID, request: Request) -> Response:
        actor = await self._authenticator.require_principal(request)
        await self._delete_step.handle(DeleteStepCommand(actor, recipe_id, step_id))
        return Response(status_code=204)

    async def upload_image(
        self,
        recipe_id: uuid.UUID,
        request: Request,
        file: Annotated[UploadFile, File()],
        alt_text: Annotated[str | None, Form(max_length=200)] = None,
    ) -> RecipeImageOut:
        actor = await self._authenticator.require_principal(request)
        data = await file.read(MAX_IMAGE_BYTES + 1)  # one byte over the limit is enough to reject it
        image_format = validate_image(file.content_type, data)
        return await self._upload_image.handle(UploadImageCommand(actor, recipe_id, data, image_format, alt_text))

    async def set_primary_image(self, recipe_id: uuid.UUID, image_id: uuid.UUID, request: Request) -> RecipeImageOut:
        actor = await self._authenticator.require_principal(request)
        return await self._set_primary_image.handle(SetPrimaryImageCommand(actor, recipe_id, image_id))

    async def delete_image(self, recipe_id: uuid.UUID, image_id: uuid.UUID, request: Request) -> Response:
        actor = await self._authenticator.require_principal(request)
        await self._delete_image.handle(DeleteImageCommand(actor, recipe_id, image_id))
        return Response(status_code=204)
