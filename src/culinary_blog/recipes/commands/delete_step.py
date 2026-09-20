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
class DeleteStepCommand(Command):
    actor: Principal
    recipe_id: uuid.UUID
    step_id: uuid.UUID


class DeleteStepHandler(CommandHandler[DeleteStepCommand, None]):
    """FR-RCP-010: soft-delete a step; the remaining steps are renumbered to stay contiguous (1, 2, 3…)."""

    def __init__(self, repository: RecipeRepository) -> None:
        self._repository = repository

    async def handle(self, command: DeleteStepCommand) -> None:
        recipe = await self._repository.get_by_id(command.recipe_id)
        if recipe is None:
            raise NotFoundError("Không tìm thấy công thức nấu ăn.")
        ensure_can_edit(command.actor, recipe)
        if await self._repository.get_step(recipe.id, command.step_id) is None:
            raise NotFoundError("Không tìm thấy bước thực hiện.")

        await self._repository.delete_step(recipe.id, command.step_id)
        logger.info(
            "recipe step deleted",
            extra={
                "user_id": str(command.actor.user_id),
                "recipe_id": str(recipe.id),
                "step_id": str(command.step_id),
                "at": datetime.now(UTC).isoformat(),
            },
        )
