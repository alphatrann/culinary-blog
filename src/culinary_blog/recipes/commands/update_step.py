import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from culinary_blog.auth.principal import Principal
from culinary_blog.cqrs import Command, CommandHandler
from culinary_blog.errors import NotFoundError
from culinary_blog.recipes.access import ensure_can_edit
from culinary_blog.recipes.repository import RecipeRepository
from culinary_blog.recipes.schemas import StepIn, StepOut

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UpdateStepCommand(Command):
    actor: Principal
    recipe_id: uuid.UUID
    step_id: uuid.UUID
    data: StepIn


class UpdateStepHandler(CommandHandler[UpdateStepCommand, StepOut]):
    """FR-RCP-010: replace a step's content; its `step_number` never changes here."""

    def __init__(self, repository: RecipeRepository) -> None:
        self._repository = repository

    async def handle(self, command: UpdateStepCommand) -> StepOut:
        recipe = await self._repository.get_by_id(command.recipe_id)
        if recipe is None:
            raise NotFoundError("Không tìm thấy công thức nấu ăn.")
        ensure_can_edit(command.actor, recipe)
        if await self._repository.get_step(recipe.id, command.step_id) is None:
            raise NotFoundError("Không tìm thấy bước thực hiện.")

        updated = await self._repository.update_step(command.step_id, command.data.model_dump())
        if updated is None:  # deleted between the lookup and the write
            raise NotFoundError("Không tìm thấy bước thực hiện.")
        logger.info(
            "recipe step updated",
            extra={
                "user_id": str(command.actor.user_id),
                "recipe_id": str(recipe.id),
                "step_id": str(updated.id),
                "at": datetime.now(UTC).isoformat(),
            },
        )
        return StepOut.model_validate(updated)
