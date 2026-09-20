from fastapi import APIRouter

from culinary_blog.auth.wiring import get_authenticator
from culinary_blog.database.session import async_session_factory
from culinary_blog.recipes.commands.create_recipe import CreateRecipeHandler
from culinary_blog.recipes.repository import RecipeRepository
from culinary_blog.recipes.router import RecipeRouter


def build_recipes_router() -> APIRouter:
    """Composition root for the recipes module: the only place that binds concrete dependencies."""
    repository = RecipeRepository(async_session_factory)
    return RecipeRouter(
        authenticator=get_authenticator(),
        create_recipe=CreateRecipeHandler(repository),
    ).router
