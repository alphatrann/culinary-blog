import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from culinary_blog.auth.principal import Principal
from culinary_blog.cqrs import Command, CommandHandler
from culinary_blog.errors import NotFoundError
from culinary_blog.recipes.access import ensure_can_edit
from culinary_blog.recipes.models import RecipeIngredient
from culinary_blog.recipes.repository import RecipeRepository
from culinary_blog.recipes.schemas import IngredientIn, IngredientOut

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AddIngredientCommand(Command):
    actor: Principal
    recipe_id: uuid.UUID
    data: IngredientIn


class AddIngredientHandler(CommandHandler[AddIngredientCommand, IngredientOut]):
    """FR-RCP-009: the owning Author or an Admin adds an ingredient; without `order_index` it goes last."""

    def __init__(self, repository: RecipeRepository) -> None:
        self._repository = repository

    async def handle(self, command: AddIngredientCommand) -> IngredientOut:
        recipe = await self._repository.get_by_id(command.recipe_id)
        if recipe is None:
            raise NotFoundError("Không tìm thấy công thức nấu ăn.")
        ensure_can_edit(command.actor, recipe)

        data = command.data
        ingredient = RecipeIngredient(
            recipe_id=recipe.id,
            name=data.name,
            quantity=data.quantity,
            unit=data.unit,
            notes=data.notes,
            order_index=data.order_index or 0,
        )
        saved = await self._repository.add_ingredient(ingredient, append=data.order_index is None)
        logger.info(
            "recipe ingredient added",
            extra={
                "user_id": str(command.actor.user_id),
                "recipe_id": str(recipe.id),
                "ingredient_id": str(saved.id),
                "at": datetime.now(UTC).isoformat(),
            },
        )
        return IngredientOut.model_validate(saved)
