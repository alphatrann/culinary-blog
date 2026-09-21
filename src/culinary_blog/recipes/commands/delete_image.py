import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from culinary_blog.auth.principal import Principal
from culinary_blog.cqrs import Command, CommandHandler
from culinary_blog.errors import NotFoundError
from culinary_blog.jobs.queue import DELETE_FILE, JobQueue
from culinary_blog.recipes.access import ensure_can_edit
from culinary_blog.recipes.repository import RecipeRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteImageCommand(Command):
    actor: Principal
    recipe_id: uuid.UUID
    image_id: uuid.UUID


class DeleteImageHandler(CommandHandler[DeleteImageCommand, None]):
    """FR-RCP-008 delete: soft-delete the record (the repository promotes another image if it was primary), then
    enqueue removal of the files from storage (FR-FILE-002)."""

    def __init__(self, repository: RecipeRepository, queue: JobQueue) -> None:
        self._repository = repository
        self._queue = queue

    async def handle(self, command: DeleteImageCommand) -> None:
        recipe = await self._repository.get_by_id(command.recipe_id)
        if recipe is None:
            raise NotFoundError("Không tìm thấy công thức nấu ăn.")
        ensure_can_edit(command.actor, recipe)

        image = await self._repository.delete_image(recipe.id, command.image_id)
        if image is None:
            raise NotFoundError("Không tìm thấy ảnh.")

        urls = [u for u in (image.original_url, image.medium_url, image.thumbnail_url) if u]
        try:
            await self._queue.enqueue(DELETE_FILE, {"urls": urls})
        except Exception:  # the record is already gone; a leaked file is only wasted space
            logger.exception("could not enqueue delete_file", extra={"image_id": str(image.id)})
        logger.info(
            "recipe image deleted",
            extra={
                "user_id": str(command.actor.user_id),
                "recipe_id": str(recipe.id),
                "image_id": str(image.id),
                "at": datetime.now(UTC).isoformat(),
            },
        )
