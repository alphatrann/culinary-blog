from dataclasses import dataclass

from culinary_blog.auth.principal import Principal
from culinary_blog.cqrs import Query, QueryHandler
from culinary_blog.errors import ForbiddenError, NotFoundError
from culinary_blog.recipes.enums import RecipeStatus
from culinary_blog.recipes.mapping import recipe_fields
from culinary_blog.recipes.repository import RecipeRepository
from culinary_blog.recipes.schemas import (
    AuthorOut,
    CategoryRefOut,
    IngredientOut,
    RecipeDetailOut,
    RecipeImageOut,
    StepOut,
)


@dataclass(frozen=True)
class GetRecipeQuery(Query):
    slug: str
    viewer: Principal | None = None


class GetRecipeHandler(QueryHandler[GetRecipeQuery, RecipeDetailOut]):
    """FR-RCP-002: full recipe by slug. Draft/archived recipes are visible only to their owner or an Admin (403)."""

    def __init__(self, repository: RecipeRepository) -> None:
        self._repository = repository

    async def handle(self, query: GetRecipeQuery) -> RecipeDetailOut:
        found = await self._repository.get_aggregate_by_slug(query.slug)
        if found is None:
            raise NotFoundError("Recipe not found")

        viewer = query.viewer
        is_owner = viewer is not None and (viewer.is_admin or viewer.user_id == found.recipe.author_id)
        if found.recipe.status != RecipeStatus.PUBLISHED and not is_owner:
            raise ForbiddenError("This recipe is not published")

        return RecipeDetailOut(
            **recipe_fields(found.recipe),  # type: ignore[arg-type]
            steps=[StepOut.model_validate(step) for step in found.steps],
            ingredients=[IngredientOut.model_validate(item) for item in found.ingredients],
            category=CategoryRefOut.model_validate(found.category),
            author=AuthorOut.model_validate(found.author),
            images=[RecipeImageOut.model_validate(image) for image in found.images],
        )
