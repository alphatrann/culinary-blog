import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from culinary_blog.auth.principal import Principal
from culinary_blog.cqrs import Command, CommandHandler
from culinary_blog.errors import NotFoundError
from culinary_blog.jobs.queue import RESIZE_IMAGE, JobQueue
from culinary_blog.recipes.access import ensure_can_edit
from culinary_blog.recipes.models import RecipeImage
from culinary_blog.recipes.repository import RecipeRepository
from culinary_blog.recipes.schemas import RecipeImageOut
from culinary_blog.storage.images import ImageFormat
from culinary_blog.storage.service import FileStorageService

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UploadImageCommand(Command):
    actor: Principal
    recipe_id: uuid.UUID
    data: bytes
    image_format: ImageFormat  # already validated (size, MIME, magic bytes) at the router boundary
    alt_text: str | None


class UploadImageHandler(CommandHandler[UploadImageCommand, RecipeImageOut]):
    """FR-RCP-008 upload: store the file, record it (first image is primary), enqueue the thumbnail job."""

    def __init__(self, repository: RecipeRepository, storage: FileStorageService, queue: JobQueue) -> None:
        self._repository = repository
        self._storage = storage
        self._queue = queue

    async def handle(self, command: UploadImageCommand) -> RecipeImageOut:
        recipe = await self._repository.get_by_id(command.recipe_id)
        if recipe is None:
            raise NotFoundError("Không tìm thấy công thức nấu ăn.")
        ensure_can_edit(command.actor, recipe)

        url = await self._storage.upload(
            command.data, f"recipes/{recipe.id}", command.image_format.extension, command.image_format.content_type
        )
        try:
            image = await self._repository.add_image(
                RecipeImage(recipe_id=recipe.id, original_url=url, alt_text=command.alt_text)
            )
        except Exception:
            await self._discard_orphan(url)
            raise

        try:
            await self._queue.enqueue(RESIZE_IMAGE, {"image_id": str(image.id), "recipe_id": str(recipe.id)})
        except Exception:  # graceful (FR-JOB-002): the original stays usable without thumbnails
            logger.exception("could not enqueue resize_image", extra={"image_id": str(image.id)})

        logger.info(
            "recipe image uploaded",
            extra={
                "user_id": str(command.actor.user_id),
                "recipe_id": str(recipe.id),
                "image_id": str(image.id),
                "at": datetime.now(UTC).isoformat(),
            },
        )
        return RecipeImageOut.model_validate(image)

    async def _discard_orphan(self, url: str) -> None:
        try:
            await self._storage.delete(url)
        except Exception:
            logger.exception("could not remove orphaned upload", extra={"url": url})
