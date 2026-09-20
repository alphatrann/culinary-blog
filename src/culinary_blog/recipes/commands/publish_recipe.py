import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from culinary_blog.auth.principal import Principal
from culinary_blog.cqrs import Command, CommandHandler
from culinary_blog.errors import NotFoundError, UnprocessableError
from culinary_blog.recipes.access import ensure_can_edit
from culinary_blog.recipes.enums import RecipeStatus
from culinary_blog.recipes.mapping import to_recipe_out
from culinary_blog.recipes.repository import RecipeRepository
from culinary_blog.recipes.schemas import RecipeOut

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PublishRecipeCommand(Command):
    actor: Principal
    recipe_id: uuid.UUID


class PublishRecipeHandler(CommandHandler[PublishRecipeCommand, RecipeOut]):
    """FR-RCP-005: publish needs ≥1 step and ≥1 ingredient (422). `published_at` is set on first publish only;
    publishing an already-published recipe is an idempotent no-op."""

    def __init__(self, repository: RecipeRepository) -> None:
        self._repository = repository

    async def handle(self, command: PublishRecipeCommand) -> RecipeOut:
        recipe = await self._repository.get_by_id(command.recipe_id)
        if recipe is None:
            raise NotFoundError("Không tìm thấy công thức nấu ăn.")
        ensure_can_edit(command.actor, recipe)

        steps, ingredients = await self._repository.get_children(recipe.id)
        if recipe.status != RecipeStatus.PUBLISHED:
            if not steps or not ingredients:
                raise UnprocessableError("Recipe phải có ít nhất 1 nguyên liệu và 1 bước thực hiện.")
            updated = await self._repository.set_status(recipe.id, RecipeStatus.PUBLISHED, stamp_published_at=True)
            if updated is None:
                raise NotFoundError("Không tìm thấy công thức nấu ăn.")
            recipe = updated
            logger.info(
                "recipe published",
                extra={
                    "user_id": str(command.actor.user_id),
                    "recipe_id": str(recipe.id),
                    "at": datetime.now(UTC).isoformat(),
                },
            )
        return to_recipe_out(recipe, steps, ingredients)
