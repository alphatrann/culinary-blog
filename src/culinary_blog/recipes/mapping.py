from culinary_blog.recipes.models import Recipe, RecipeIngredient, RecipeStep
from culinary_blog.recipes.schemas import IngredientOut, NutritionOut, RecipeOut, StepOut

_NESTED = {"nutrition", "steps", "ingredients"}


def recipe_fields(recipe: Recipe) -> dict[str, object]:
    """The `RecipeOut` scalar fields plus nutrition; steps/ingredients are supplied by the caller."""
    return {
        **recipe.model_dump(include=set(RecipeOut.model_fields) - _NESTED),
        "nutrition": NutritionOut(**{name: getattr(recipe, f"nutrition_{name}") for name in NutritionOut.model_fields}),
    }


def to_recipe_out(recipe: Recipe, steps: list[RecipeStep], ingredients: list[RecipeIngredient]) -> RecipeOut:
    return RecipeOut(
        **recipe_fields(recipe),  # type: ignore[arg-type]
        steps=[StepOut.model_validate(step) for step in sorted(steps, key=lambda step: step.step_number)],
        ingredients=[
            IngredientOut.model_validate(item) for item in sorted(ingredients, key=lambda item: item.order_index)
        ],
    )
