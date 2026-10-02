from fastapi import APIRouter

from culinary_blog.auth.wiring import get_authenticator
from culinary_blog.cache.redis import get_cache_redis
from culinary_blog.cache.service import RedisCache
from culinary_blog.categories.cache import CategoryCacheInvalidator
from culinary_blog.categories.commands.create_category import CreateCategoryHandler
from culinary_blog.categories.commands.update_category import UpdateCategoryHandler
from culinary_blog.categories.queries.get_category import GetCategoryHandler
from culinary_blog.categories.queries.list_categories import ListCategoriesHandler
from culinary_blog.categories.repository import CategoryRepository
from culinary_blog.categories.router import CategoryRouter
from culinary_blog.config import get_settings
from culinary_blog.database.session import async_session_factory, read_session_factory


def build_categories_router() -> APIRouter:
    """Composition root for the categories module: the only place that binds concrete dependencies."""
    repository = CategoryRepository(async_session_factory, read_session_factory)
    settings = get_settings()
    cache = RedisCache(get_cache_redis())
    invalidator = CategoryCacheInvalidator(cache)
    return CategoryRouter(
        authenticator=get_authenticator(),
        create_category=CreateCategoryHandler(repository, invalidator),
        update_category=UpdateCategoryHandler(repository, invalidator),
        list_categories=ListCategoriesHandler(repository, cache, settings.cache_ttl_categories_seconds),
        get_category=GetCategoryHandler(repository, cache, settings.cache_ttl_recipes_seconds),
    ).router
