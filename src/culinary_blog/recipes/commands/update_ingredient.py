import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from culinary_blog.auth.principal import Principal
from culinary_blog.cqrs import Command, CommandHandler
from culinary_blog.errors import NotFoundError
from culinary_blog.recipes.access import ensure_can_edit
from culinary_blog.recipes.repository import RecipeRepository
from culinary_blog.recipes.schemas import IngredientIn, IngredientOut

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UpdateIngredientCommand(Command):
    actor: Principal
    recipe_id: uuid.UUID
    ingredient_id: uuid.UUID
    data: IngredientIn


class UpdateIngredientHandler(CommandHandler[UpdateIngredientCommand, IngredientOut]):
    """FR-RCP-009: replace an ingredient's fields (an omitted `order_index` keeps the current position)."""

    def __init__(self, repository: RecipeRepository) -> None:
        self._repository = repository

    async def handle(self, command: UpdateIngredientCommand) -> IngredientOut:
        recipe = await self._repository.get_by_id(command.recipe_id)
        if recipe is None:
            raise NotFoundError("Không tìm thấy công thức nấu ăn.")
        ensure_can_edit(command.actor, recipe)
        if await self._repository.get_ingredient(recipe.id, command.ingredient_id) is None:
            raise NotFoundError("Không tìm thấy nguyên liệu.")

        values: dict[str, object] = {
            "name": command.data.name,
            "quantity": command.data.quantity,
            "unit": command.data.unit,
            "notes": command.data.notes,
        }
        if command.data.order_index is not None:
            values["order_index"] = command.data.order_index
        updated = await self._repository.update_ingredient(command.ingredient_id, values)
        if updated is None:  # deleted between the lookup and the write
            raise NotFoundError("Không tìm thấy nguyên liệu.")
        logger.info(
            "recipe ingredient updated",
            extra={
                "user_id": str(command.actor.user_id),
                "recipe_id": str(recipe.id),
                "ingredient_id": str(updated.id),
                "at": datetime.now(UTC).isoformat(),
            },
        )
        return IngredientOut.model_validate(updated)
