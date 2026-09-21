import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from culinary_blog.auth.principal import Principal
from culinary_blog.cqrs import Command, CommandHandler
from culinary_blog.errors import NotFoundError
from culinary_blog.recipes.access import ensure_can_edit
from culinary_blog.recipes.repository import RecipeRepository
from culinary_blog.recipes.schemas import RecipeImageOut

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SetPrimaryImageCommand(Command):
    actor: Principal
    recipe_id: uuid.UUID
    image_id: uuid.UUID


class SetPrimaryImageHandler(CommandHandler[SetPrimaryImageCommand, RecipeImageOut]):
    """FR-RCP-008 set primary: exactly one live image of the recipe is primary afterwards. Idempotent."""

    def __init__(self, repository: RecipeRepository) -> None:
        self._repository = repository

    async def handle(self, command: SetPrimaryImageCommand) -> RecipeImageOut:
        recipe = await self._repository.get_by_id(command.recipe_id)
        if recipe is None:
            raise NotFoundError("Không tìm thấy công thức nấu ăn.")
        ensure_can_edit(command.actor, recipe)
        if await self._repository.get_image(recipe.id, command.image_id) is None:
            raise NotFoundError("Không tìm thấy ảnh.")

        image = await self._repository.set_primary_image(recipe.id, command.image_id)
        if image is None:  # deleted between the check and the update
            raise NotFoundError("Không tìm thấy ảnh.")
        logger.info(
            "recipe primary image set",
            extra={
                "user_id": str(command.actor.user_id),
                "recipe_id": str(recipe.id),
                "image_id": str(image.id),
                "at": datetime.now(UTC).isoformat(),
            },
        )
        return RecipeImageOut.model_validate(image)
