import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from culinary_blog.auth.principal import Principal
from culinary_blog.categories.slug import slugify
from culinary_blog.cqrs import Command, CommandHandler
from culinary_blog.errors import ForbiddenError, UnprocessableError
from culinary_blog.recipes.enums import RecipeDifficulty, RecipeStatus
from culinary_blog.recipes.mapping import to_recipe_out
from culinary_blog.recipes.models import Recipe, RecipeIngredient, RecipeStep
from culinary_blog.recipes.repository import RecipeRepository
from culinary_blog.recipes.schemas import IngredientIn, NutritionIn, RecipeOut, StepIn

logger = logging.getLogger(__name__)

_SLUG_BASE_MAX = 200  # leaves room under the 220-char column for a numeric suffix


@dataclass(frozen=True)
class CreateRecipeCommand(Command):
    actor: Principal
    title: str
    description: str
    category_id: uuid.UUID
    prep_time_minutes: int
    cook_time_minutes: int
    servings: int
    difficulty: RecipeDifficulty = RecipeDifficulty.EASY
    nutrition: NutritionIn | None = None
    steps: list[StepIn] = field(default_factory=list)
    ingredients: list[IngredientIn] = field(default_factory=list)


class CreateRecipeHandler(CommandHandler[CreateRecipeCommand, RecipeOut]):
    """FR-RCP-003: an Author/Admin creates a draft recipe, optionally with nested steps, ingredients and nutrition."""

    def __init__(self, repository: RecipeRepository) -> None:
        self._repository = repository

    async def handle(self, command: CreateRecipeCommand) -> RecipeOut:
        if not command.actor.can_write_recipes:
            raise ForbiddenError("Author or Admin role required")
        if not await self._repository.category_exists(command.category_id):
            raise UnprocessableError("Category không hợp lệ")

        nutrition = (command.nutrition or NutritionIn()).model_dump()
        recipe = Recipe(
            title=command.title,
            slug=await self._unique_slug(command.title),
            description=command.description,
            prep_time_minutes=command.prep_time_minutes,
            cook_time_minutes=command.cook_time_minutes,
            servings=command.servings,
            difficulty=command.difficulty,
            status=RecipeStatus.DRAFT,
            category_id=command.category_id,
            author_id=command.actor.user_id,
            **{f"nutrition_{name}": value for name, value in nutrition.items()},
        )
        steps = [
            RecipeStep(recipe_id=recipe.id, step_number=number, **step.model_dump())
            for number, step in enumerate(command.steps, start=1)
        ]
        ingredients = [
            RecipeIngredient(
                recipe_id=recipe.id,
                name=ingredient.name,
                quantity=ingredient.quantity,
                unit=ingredient.unit,
                notes=ingredient.notes,
                # a missing order_index defaults to the ingredient's position in the request
                order_index=position if ingredient.order_index is None else ingredient.order_index,
            )
            for position, ingredient in enumerate(command.ingredients)
        ]
        await self._repository.add(recipe, steps, ingredients)
        logger.info(
            "recipe created",
            extra={
                "user_id": str(command.actor.user_id),
                "recipe_id": str(recipe.id),
                "at": datetime.now(UTC).isoformat(),
            },
        )
        return to_recipe_out(recipe, steps, ingredients)

    async def _unique_slug(self, title: str) -> str:
        base = slugify(title)[:_SLUG_BASE_MAX].strip("-") or "recipe"
        slug, suffix = base, 1
        while await self._repository.slug_taken(slug):
            suffix += 1
            slug = f"{base}-{suffix}"
        return slug
