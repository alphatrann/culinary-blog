import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from culinary_blog.auth.principal import Principal
from culinary_blog.cqrs import Command, CommandHandler
from culinary_blog.errors import ConflictError, ForbiddenError, NotFoundError
from culinary_blog.recipes.enums import RecipeDifficulty
from culinary_blog.recipes.mapping import to_recipe_out
from culinary_blog.recipes.repository import RecipeRepository
from culinary_blog.recipes.schemas import NutritionIn, RecipeOut

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UpdateRecipeCommand(Command):
    actor: Principal
    recipe_id: uuid.UUID
    expected_version: int
    title: str
    description: str
    category_id: uuid.UUID
    prep_time_minutes: int
    cook_time_minutes: int
    servings: int
    difficulty: RecipeDifficulty = RecipeDifficulty.EASY
    nutrition: NutritionIn | None = None


class UpdateRecipeHandler(CommandHandler[UpdateRecipeCommand, RecipeOut]):
    """FR-RCP-004: the owning Author or an Admin updates a recipe's own fields.

    Guarded by optimistic concurrency: the client's `If-Match` row_version must still be current, else 409. The slug,
    status and steps/ingredients are not touched; nutrition is replaced only when supplied.
    """

    def __init__(self, repository: RecipeRepository) -> None:
        self._repository = repository

    async def handle(self, command: UpdateRecipeCommand) -> RecipeOut:
        actor = command.actor
        existing = await self._repository.get_by_id(command.recipe_id)
        if existing is None:
            raise NotFoundError("Không tìm thấy công thức nấu ăn.")
        if not (actor.is_admin or (actor.can_write_recipes and existing.author_id == actor.user_id)):
            raise ForbiddenError("Only the recipe's author or an Admin can update it")

        values: dict[str, object] = {
            "title": command.title,
            "description": command.description,
            "category_id": command.category_id,
            "prep_time_minutes": command.prep_time_minutes,
            "cook_time_minutes": command.cook_time_minutes,
            "servings": command.servings,
            "difficulty": command.difficulty,
        }
        if command.nutrition is not None:
            values.update({f"nutrition_{name}": value for name, value in command.nutrition.model_dump().items()})

        recipe = await self._repository.update(command.recipe_id, command.expected_version, values)
        if recipe is None:
            raise ConflictError("Dữ liệu đã bị thay đổi bởi người dùng khác.")

        logger.info(
            "recipe updated",
            extra={
                "user_id": str(actor.user_id),
                "recipe_id": str(recipe.id),
                "at": datetime.now(UTC).isoformat(),
            },
        )
        steps, ingredients = await self._repository.get_children(recipe.id)
        return to_recipe_out(recipe, steps, ingredients)
