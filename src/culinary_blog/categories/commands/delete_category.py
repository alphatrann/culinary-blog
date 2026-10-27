import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from culinary_blog.auth.principal import Principal
from culinary_blog.categories.cache import CategoryCacheInvalidator
from culinary_blog.categories.repository import CategoryRepository
from culinary_blog.cqrs import Command, CommandHandler
from culinary_blog.errors import ConflictError, ForbiddenError, NotFoundError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteCategoryCommand(Command):
    actor: Principal
    category_id: uuid.UUID


class DeleteCategoryHandler(CommandHandler[DeleteCategoryCommand, None]):
    """FR-CAT-005: Admin soft-deletes a category, unless any non-deleted recipe (any status) still references it."""

    def __init__(self, repository: CategoryRepository, cache: CategoryCacheInvalidator) -> None:
        self._repository = repository
        self._cache = cache

    async def handle(self, command: DeleteCategoryCommand) -> None:
        if not command.actor.is_admin:
            raise ForbiddenError("Admin role required")
        category = await self._repository.get_by_id(command.category_id)
        if category is None:
            raise NotFoundError("Category not found")
        count = await self._repository.count_recipes(category.id)
        if count > 0:
            raise ConflictError(f"Category still has {count} recipe(s); reassign or delete them first")

        category.is_deleted = True
        await self._repository.save(category)
        await self._cache.deleted()
        logger.info(
            "category deleted",
            extra={
                "user_id": str(command.actor.user_id),
                "category_id": str(category.id),
                "at": datetime.now(UTC).isoformat(),
            },
        )
