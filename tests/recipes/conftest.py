from datetime import timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from culinary_blog.auth.dependencies import Authenticator
from culinary_blog.auth.security import TokenService
from culinary_blog.problem_details import register_problem_handlers
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
from culinary_blog.recipes.router import RecipeRouter
from tests.cache.fakes import FakeCache
from tests.recipes.fakes import FakeJobQueue, FakeRecipeRepository, FakeStorage, invalidator

TOKENS = TokenService("test-secret-key-at-least-32-bytes-long", timedelta(minutes=15), timedelta(days=7))


@pytest.fixture
def repo() -> FakeRecipeRepository:
    return FakeRecipeRepository()


@pytest.fixture
def cache() -> FakeCache:
    return FakeCache()


@pytest.fixture
def storage() -> FakeStorage:
    return FakeStorage()


@pytest.fixture
def queue() -> FakeJobQueue:
    return FakeJobQueue()


@pytest.fixture
def category_id(repo) -> str:
    return str(repo.add_category())


@pytest.fixture
def client(repo, storage, queue, cache) -> TestClient:
    router = RecipeRouter(
        authenticator=Authenticator(TOKENS),
        create_recipe=CreateRecipeHandler(repo, invalidator(cache)),
        update_recipe=UpdateRecipeHandler(repo, invalidator(cache)),
        list_recipes=ListRecipesHandler(repo, cache),
        search_recipes=SearchRecipesHandler(repo, cache),
        get_recipe=GetRecipeHandler(repo, cache),
        publish_recipe=PublishRecipeHandler(repo, invalidator(cache)),
        unpublish_recipe=UnpublishRecipeHandler(repo, invalidator(cache)),
        delete_recipe=DeleteRecipeHandler(repo, invalidator(cache)),
        add_ingredient=AddIngredientHandler(repo, invalidator(cache)),
        update_ingredient=UpdateIngredientHandler(repo, invalidator(cache)),
        delete_ingredient=DeleteIngredientHandler(repo, invalidator(cache)),
        add_step=AddStepHandler(repo, invalidator(cache)),
        update_step=UpdateStepHandler(repo, invalidator(cache)),
        delete_step=DeleteStepHandler(repo, invalidator(cache)),
        upload_image=UploadImageHandler(repo, storage, queue, invalidator(cache)),
        set_primary_image=SetPrimaryImageHandler(repo, invalidator(cache)),
        delete_image=DeleteImageHandler(repo, queue, invalidator(cache)),
    ).router
    app = FastAPI()
    register_problem_handlers(app)
    app.include_router(router)
    return TestClient(app)
