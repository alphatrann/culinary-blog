"""Shared pieces for list/search/category views: the extra columns a recipe card needs and how to map them."""

from sqlalchemy import ColumnElement, func, select
from sqlmodel import col

from culinary_blog.auth.models import User
from culinary_blog.categories.models import Category
from culinary_blog.categories.schemas import RecipeSummaryOut
from culinary_blog.recipes.models import Recipe, RecipeImage

_EXTRA_FIELDS = {"category_name", "category_slug", "author_name", "thumbnail_url"}


def thumbnail_column() -> ColumnElement[str | None]:
    """Correlated subquery: the recipe's primary (else first) image, thumbnail preferred over the original."""
    return (
        select(func.coalesce(RecipeImage.thumbnail_url, RecipeImage.original_url))
        .where(col(RecipeImage.recipe_id) == col(Recipe.id), col(RecipeImage.is_deleted).is_(False))
        .order_by(col(RecipeImage.is_primary).desc(), col(RecipeImage.order_index), col(RecipeImage.created_at))
        .limit(1)
        .scalar_subquery()
    )


# Select these alongside `Recipe`, joined to Category and User, then pass the row to `to_summary`.
def extra_columns() -> tuple[ColumnElement[str], ColumnElement[str], ColumnElement[str], ColumnElement[str | None]]:
    return (col(Category.name), col(Category.slug), col(User.display_name), thumbnail_column())


def to_summary(
    recipe: Recipe, category_name: str, category_slug: str, author_name: str, thumbnail_url: str | None
) -> RecipeSummaryOut:
    return RecipeSummaryOut(
        **recipe.model_dump(include=set(RecipeSummaryOut.model_fields) - _EXTRA_FIELDS),
        category_name=category_name,
        category_slug=category_slug,
        author_name=author_name,
        thumbnail_url=thumbnail_url,
    )
