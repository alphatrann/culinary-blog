import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from culinary_blog.auth.principal import Principal
from culinary_blog.cqrs import Command, CommandHandler
from culinary_blog.errors import NotFoundError
from culinary_blog.recipes.access import ensure_can_edit
from culinary_blog.recipes.models import RecipeStep
from culinary_blog.recipes.repository import RecipeRepository
from culinary_blog.recipes.schemas import StepIn, StepOut

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AddStepCommand(Command):
    actor: Principal
    recipe_id: uuid.UUID
    data: StepIn


class AddStepHandler(CommandHandler[AddStepCommand, StepOut]):
    """FR-RCP-010: add a step; the repository assigns `step_number = max + 1` (the client never sends it)."""

    def __init__(self, repository: RecipeRepository) -> None:
        self._repository = repository

    async def handle(self, command: AddStepCommand) -> StepOut:
        recipe = await self._repository.get_by_id(command.recipe_id)
        if recipe is None:
            raise NotFoundError("Không tìm thấy công thức nấu ăn.")
        ensure_can_edit(command.actor, recipe)

        saved = await self._repository.add_step(
            RecipeStep(recipe_id=recipe.id, step_number=0, **command.data.model_dump())
        )
        logger.info(
            "recipe step added",
            extra={
                "user_id": str(command.actor.user_id),
                "recipe_id": str(recipe.id),
                "step_id": str(saved.id),
                "at": datetime.now(UTC).isoformat(),
            },
        )
        return StepOut.model_validate(saved)
