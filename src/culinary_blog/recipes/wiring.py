from fastapi import APIRouter

from culinary_blog.auth.wiring import get_authenticator
from culinary_blog.cache.redis import get_cache_redis, get_queue_redis
from culinary_blog.cache.service import RedisCache
from culinary_blog.config import get_settings
from culinary_blog.database.session import async_session_factory, read_session_factory
from culinary_blog.jobs.queue import RedisJobQueue
from culinary_blog.recipes.cache import RecipeCacheInvalidator
from culinary_blog.recipes.commands.add_ingredient import AddIngredientHandler
from culinary_blog.recipes.commands.add_step import AddStepHandler
from culinary_blog.recipes.commands.create_recipe import CreateRecipeHandler
from culinary_blog.recipes.commands.delete_image import DeleteImageHandler
from culinary_blog.recipes.commands.delete_ingredient import DeleteIngredientHandler
from culinary_blog.recipes.commands.delete_recipe import DeleteRecipeHandler
from culinary_blog.recipes.commands.delete_step import DeleteStepHandler
from culinary_blog.recipes.commands.publish_recipe import PublishRecipeHandler
from culinary_blog.recipes.commands.set_primary_image import SetPrimaryImageHandler
from culinary_blog.recipes.commands.unpublish_recipe import UnpublishRecipeHandler
from culinary_blog.recipes.commands.update_ingredient import UpdateIngredientHandler
from culinary_blog.recipes.commands.update_recipe import UpdateRecipeHandler
from culinary_blog.recipes.commands.update_step import UpdateStepHandler
from culinary_blog.recipes.commands.upload_image import UploadImageHandler
from culinary_blog.recipes.queries.get_recipe import GetRecipeHandler
from culinary_blog.recipes.queries.list_recipes import ListRecipesHandler
from culinary_blog.recipes.queries.search_recipes import SearchRecipesHandler
from culinary_blog.recipes.repository import RecipeRepository
from culinary_blog.recipes.router import RecipeRouter
from culinary_blog.storage.minio_storage import MinioFileStorage


def build_recipes_router() -> APIRouter:
    """Composition root for the recipes module: the only place that binds concrete dependencies."""
    repository = RecipeRepository(async_session_factory, read_session_factory)
    storage = MinioFileStorage(get_settings())
    queue = RedisJobQueue(get_queue_redis())
    settings = get_settings()
    cache = RedisCache(get_cache_redis())
    invalidator = RecipeCacheInvalidator(cache)
    return RecipeRouter(
        authenticator=get_authenticator(),
        create_recipe=CreateRecipeHandler(repository, invalidator),
        update_recipe=UpdateRecipeHandler(repository, invalidator),
        list_recipes=ListRecipesHandler(repository, cache, settings.cache_ttl_recipes_seconds),
        search_recipes=SearchRecipesHandler(repository, cache, settings.cache_ttl_search_seconds),
        get_recipe=GetRecipeHandler(repository, cache, settings.cache_ttl_recipes_seconds),
        publish_recipe=PublishRecipeHandler(repository, invalidator),
        unpublish_recipe=UnpublishRecipeHandler(repository, invalidator),
        delete_recipe=DeleteRecipeHandler(repository, invalidator),
        add_ingredient=AddIngredientHandler(repository, invalidator),
        update_ingredient=UpdateIngredientHandler(repository, invalidator),
        delete_ingredient=DeleteIngredientHandler(repository, invalidator),
        add_step=AddStepHandler(repository, invalidator),
        update_step=UpdateStepHandler(repository, invalidator),
        delete_step=DeleteStepHandler(repository, invalidator),
        upload_image=UploadImageHandler(repository, storage, queue, invalidator),
        set_primary_image=SetPrimaryImageHandler(repository, invalidator),
        delete_image=DeleteImageHandler(repository, queue, invalidator),
    ).router
