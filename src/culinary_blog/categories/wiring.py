from fastapi import APIRouter

from culinary_blog.auth.wiring import get_authenticator
from culinary_blog.categories.commands.create_category import CreateCategoryHandler
from culinary_blog.categories.commands.update_category import UpdateCategoryHandler
from culinary_blog.categories.queries.get_category import GetCategoryHandler
from culinary_blog.categories.queries.list_categories import ListCategoriesHandler
from culinary_blog.categories.repository import CategoryRepository
from culinary_blog.categories.router import CategoryRouter
from culinary_blog.database.session import async_session_factory


def build_categories_router() -> APIRouter:
    """Composition root for the categories module: the only place that binds concrete dependencies."""
    repository = CategoryRepository(async_session_factory)
    return CategoryRouter(
        authenticator=get_authenticator(),
        create_category=CreateCategoryHandler(repository),
        update_category=UpdateCategoryHandler(repository),
        list_categories=ListCategoriesHandler(repository),
        get_category=GetCategoryHandler(repository),
    ).router
