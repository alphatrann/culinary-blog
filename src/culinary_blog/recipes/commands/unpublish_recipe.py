import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from culinary_blog.auth.principal import Principal
from culinary_blog.cqrs import Command, CommandHandler
from culinary_blog.errors import NotFoundError
from culinary_blog.recipes.access import ensure_can_edit
from culinary_blog.recipes.enums import RecipeStatus
from culinary_blog.recipes.mapping import to_recipe_out
from culinary_blog.recipes.repository import RecipeRepository
from culinary_blog.recipes.schemas import RecipeOut

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UnpublishRecipeCommand(Command):
    actor: Principal
    recipe_id: uuid.UUID


class UnpublishRecipeHandler(CommandHandler[UnpublishRecipeCommand, RecipeOut]):
    """FR-RCP-005: move a published recipe back to draft (`published_at` is kept); idempotent if already a draft."""

    def __init__(self, repository: RecipeRepository) -> None:
        self._repository = repository

    async def handle(self, command: UnpublishRecipeCommand) -> RecipeOut:
        recipe = await self._repository.get_by_id(command.recipe_id)
        if recipe is None:
            raise NotFoundError("Không tìm thấy công thức nấu ăn.")
        ensure_can_edit(command.actor, recipe)

        if recipe.status != RecipeStatus.DRAFT:
            updated = await self._repository.set_status(recipe.id, RecipeStatus.DRAFT, stamp_published_at=False)
            if updated is None:
                raise NotFoundError("Không tìm thấy công thức nấu ăn.")
            recipe = updated
            logger.info(
                "recipe unpublished",
                extra={
                    "user_id": str(command.actor.user_id),
                    "recipe_id": str(recipe.id),
                    "at": datetime.now(UTC).isoformat(),
                },
            )
        steps, ingredients = await self._repository.get_children(recipe.id)
        return to_recipe_out(recipe, steps, ingredients)
