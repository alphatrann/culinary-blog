import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from culinary_blog.auth.principal import Principal
from culinary_blog.cqrs import Command, CommandHandler
from culinary_blog.errors import NotFoundError
from culinary_blog.recipes.access import ensure_can_edit
from culinary_blog.recipes.repository import RecipeRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteIngredientCommand(Command):
    actor: Principal
    recipe_id: uuid.UUID
    ingredient_id: uuid.UUID


class DeleteIngredientHandler(CommandHandler[DeleteIngredientCommand, None]):
    """FR-RCP-009: soft-delete an ingredient."""

    def __init__(self, repository: RecipeRepository) -> None:
        self._repository = repository

    async def handle(self, command: DeleteIngredientCommand) -> None:
        recipe = await self._repository.get_by_id(command.recipe_id)
        if recipe is None:
            raise NotFoundError("Không tìm thấy công thức nấu ăn.")
        ensure_can_edit(command.actor, recipe)
        if await self._repository.get_ingredient(recipe.id, command.ingredient_id) is None:
            raise NotFoundError("Không tìm thấy nguyên liệu.")

        await self._repository.delete_ingredient(command.ingredient_id)
        logger.info(
            "recipe ingredient deleted",
            extra={
                "user_id": str(command.actor.user_id),
                "recipe_id": str(recipe.id),
                "ingredient_id": str(command.ingredient_id),
                "at": datetime.now(UTC).isoformat(),
            },
        )
