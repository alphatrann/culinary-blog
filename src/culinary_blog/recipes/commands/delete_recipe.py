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
class DeleteRecipeCommand(Command):
    actor: Principal
    recipe_id: uuid.UUID


class DeleteRecipeHandler(CommandHandler[DeleteRecipeCommand, None]):
    """FR-RCP-007: an Author/Admin soft-deletes a recipe, cascading to its steps, ingredients and images.

    Image files are NOT removed from storage here (only via explicit image deletion or the cleanup job)."""

    def __init__(self, repository: RecipeRepository) -> None:
        self._repository = repository

    async def handle(self, command: DeleteRecipeCommand) -> None:
        recipe = await self._repository.get_by_id(command.recipe_id)
        if recipe is None:
            raise NotFoundError("Không tìm thấy công thức nấu ăn.")
        ensure_can_edit(command.actor, recipe)

        deleted = await self._repository.delete(command.recipe_id)
        if deleted is None:
            raise NotFoundError("Không tìm thấy công thức nấu ăn.")

        logger.info(
            "recipe deleted",
            extra={
                "user_id": str(command.actor.user_id),
                "recipe_id": str(command.recipe_id),
                "at": datetime.now(UTC).isoformat(),
            },
        )
