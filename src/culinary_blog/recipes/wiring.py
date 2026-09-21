from fastapi import APIRouter

from culinary_blog.auth.wiring import get_authenticator
from culinary_blog.cache.redis import get_queue_redis
from culinary_blog.config import get_settings
from culinary_blog.database.session import async_session_factory
from culinary_blog.jobs.queue import RedisJobQueue
from culinary_blog.recipes.commands.add_ingredient import AddIngredientHandler
from culinary_blog.recipes.commands.add_step import AddStepHandler
from culinary_blog.recipes.commands.create_recipe import CreateRecipeHandler
from culinary_blog.recipes.commands.delete_image import DeleteImageHandler
from culinary_blog.recipes.commands.delete_ingredient import DeleteIngredientHandler
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
from culinary_blog.recipes.repository import RecipeRepository
from culinary_blog.recipes.router import RecipeRouter
from culinary_blog.storage.minio_storage import MinioFileStorage


def build_recipes_router() -> APIRouter:
    """Composition root for the recipes module: the only place that binds concrete dependencies."""
    repository = RecipeRepository(async_session_factory)
    storage = MinioFileStorage(get_settings())
    queue = RedisJobQueue(get_queue_redis())
    return RecipeRouter(
        authenticator=get_authenticator(),
        create_recipe=CreateRecipeHandler(repository),
        update_recipe=UpdateRecipeHandler(repository),
        list_recipes=ListRecipesHandler(repository),
        get_recipe=GetRecipeHandler(repository),
        publish_recipe=PublishRecipeHandler(repository),
        unpublish_recipe=UnpublishRecipeHandler(repository),
        add_ingredient=AddIngredientHandler(repository),
        update_ingredient=UpdateIngredientHandler(repository),
        delete_ingredient=DeleteIngredientHandler(repository),
        add_step=AddStepHandler(repository),
        update_step=UpdateStepHandler(repository),
        delete_step=DeleteStepHandler(repository),
        upload_image=UploadImageHandler(repository, storage, queue),
        set_primary_image=SetPrimaryImageHandler(repository),
        delete_image=DeleteImageHandler(repository, queue),
    ).router
