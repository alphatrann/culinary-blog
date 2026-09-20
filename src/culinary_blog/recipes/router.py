from fastapi import APIRouter, Request, Response

from culinary_blog.auth.dependencies import Authenticator
from culinary_blog.recipes.commands.create_recipe import CreateRecipeCommand, CreateRecipeHandler
from culinary_blog.recipes.schemas import RecipeCreateRequest, RecipeOut


class RecipeRouter:
    """HTTP adapter for recipes: authenticates, builds commands/queries, delegates to handlers."""

    def __init__(self, authenticator: Authenticator, create_recipe: CreateRecipeHandler) -> None:
        self._authenticator = authenticator
        self._create_recipe = create_recipe

        self.router = APIRouter(prefix="/api/v1/recipes", tags=["recipes"])
        self.router.add_api_route("", self.create, methods=["POST"], response_model=RecipeOut, status_code=201)

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
        return recipe
