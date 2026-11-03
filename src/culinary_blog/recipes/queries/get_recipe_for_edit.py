import uuid
from dataclasses import dataclass

from culinary_blog.auth.principal import Principal
from culinary_blog.cqrs import Query, QueryHandler
from culinary_blog.errors import ForbiddenError, NotFoundError
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
class GetRecipeForEditQuery(Query):
    recipe_id: uuid.UUID
    actor: Principal


class GetRecipeForEditHandler(QueryHandler[GetRecipeForEditQuery, RecipeDetailOut]):
    """Edit-form read by id: the owning Author or an Admin, drafts and unpublished changes included.

    Not cached. It is read once when an edit page opens, and the cache holds only the public slug view.
    """

    def __init__(self, repository: RecipeRepository) -> None:
        self._repository = repository

    async def handle(self, query: GetRecipeForEditQuery) -> RecipeDetailOut:
        found = await self._repository.get_aggregate_by_id(query.recipe_id)
        if found is None:
            raise NotFoundError("Không tìm thấy công thức nấu ăn.")
        actor = query.actor
        if not (actor.is_admin or actor.user_id == found.recipe.author_id):
            raise ForbiddenError("Only the recipe's author or an Admin can view it for editing")
        return RecipeDetailOut(
            **recipe_fields(found.recipe),  # type: ignore[arg-type]
            steps=[StepOut.model_validate(step) for step in found.steps],
            ingredients=[IngredientOut.model_validate(item) for item in found.ingredients],
            category=CategoryRefOut.model_validate(found.category),
            author=AuthorOut.model_validate(found.author),
            images=[RecipeImageOut.model_validate(image) for image in found.images],
        )
