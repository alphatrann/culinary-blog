from culinary_blog.auth.principal import Principal
from culinary_blog.errors import ForbiddenError
from culinary_blog.recipes.models import Recipe


def ensure_can_edit(actor: Principal, recipe: Recipe) -> None:
    """Only the owning Author or an Admin may change a recipe (and its steps/ingredients)."""
    if not (actor.is_admin or (actor.can_write_recipes and recipe.author_id == actor.user_id)):
        raise ForbiddenError("Only the recipe's author or an Admin can modify it")
