import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from culinary_blog.auth.principal import Principal
from culinary_blog.categories.models import Category
from culinary_blog.categories.repository import CategoryRepository
from culinary_blog.categories.schemas import CategoryOut
from culinary_blog.categories.slug import slugify
from culinary_blog.cqrs import Command, CommandHandler
from culinary_blog.errors import ConflictError, ForbiddenError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreateCategoryCommand(Command):
    actor: Principal
    name: str
    description: str | None = None
    image_url: str | None = None


class CreateCategoryHandler(CommandHandler[CreateCategoryCommand, CategoryOut]):
    """FR-CAT-003: Admin creates a category; the slug is derived from the name and made unique with a numeric suffix."""

    def __init__(self, repository: CategoryRepository) -> None:
        self._repository = repository

    async def handle(self, command: CreateCategoryCommand) -> CategoryOut:
        if not command.actor.is_admin:
            raise ForbiddenError("Admin role required")
        if await self._repository.name_taken(command.name):
            raise ConflictError("A category with this name already exists")

        category = Category(
            name=command.name,
            slug=await self._unique_slug(command.name),
            description=command.description,
            image_url=command.image_url,
        )
        await self._repository.add(category)
        logger.info(
            "category created",
            extra={
                "user_id": str(command.actor.user_id),
                "category_id": str(category.id),
                "at": datetime.now(UTC).isoformat(),
            },
        )
        return CategoryOut(**category.model_dump(include=set(CategoryOut.model_fields) - {"recipe_count"}))

    async def _unique_slug(self, name: str) -> str:
        base = slugify(name) or "category"
        slug, suffix = base, 1
        while await self._repository.slug_taken(slug):
            suffix += 1
            slug = f"{base}-{suffix}"
        return slug
