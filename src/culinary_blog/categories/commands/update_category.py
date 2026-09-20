import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from culinary_blog.auth.principal import Principal
from culinary_blog.categories.repository import CategoryRepository
from culinary_blog.categories.schemas import CategoryOut
from culinary_blog.cqrs import Command, CommandHandler
from culinary_blog.errors import ConflictError, ForbiddenError, NotFoundError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UpdateCategoryCommand(Command):
    actor: Principal
    category_id: uuid.UUID
    name: str
    description: str | None
    image_url: str | None
    order_index: int


class UpdateCategoryHandler(CommandHandler[UpdateCategoryCommand, CategoryOut]):
    """FR-CAT-004: Admin edits a category. The slug never changes on rename, so existing links keep working."""

    def __init__(self, repository: CategoryRepository) -> None:
        self._repository = repository

    async def handle(self, command: UpdateCategoryCommand) -> CategoryOut:
        if not command.actor.is_admin:
            raise ForbiddenError("Admin role required")
        category = await self._repository.get_by_id(command.category_id)
        if category is None:
            raise NotFoundError("Category not found")
        if await self._repository.name_taken(command.name, excluding=category.id):
            raise ConflictError("A category with this name already exists")

        category.name = command.name
        category.description = command.description
        category.image_url = command.image_url
        category.order_index = command.order_index
        await self._repository.save(category)
        logger.info(
            "category updated",
            extra={
                "user_id": str(command.actor.user_id),
                "category_id": str(category.id),
                "at": datetime.now(UTC).isoformat(),
            },
        )
        recipe_count = await self._repository.count_published_recipes(category.id)
        return CategoryOut(
            **category.model_dump(include=set(CategoryOut.model_fields) - {"recipe_count"}), recipe_count=recipe_count
        )
