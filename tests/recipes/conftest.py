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
from tests.recipes.fakes import FakeJobQueue, FakeRecipeRepository, FakeStorage

TOKENS = TokenService("test-secret-key-at-least-32-bytes-long", timedelta(minutes=15), timedelta(days=7))


@pytest.fixture
def repo() -> FakeRecipeRepository:
    return FakeRecipeRepository()


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
def client(repo, storage, queue) -> TestClient:
    router = RecipeRouter(
        authenticator=Authenticator(TOKENS),
        create_recipe=CreateRecipeHandler(repo),
        update_recipe=UpdateRecipeHandler(repo),
        list_recipes=ListRecipesHandler(repo),
        search_recipes=SearchRecipesHandler(repo),
        get_recipe=GetRecipeHandler(repo),
        publish_recipe=PublishRecipeHandler(repo),
        unpublish_recipe=UnpublishRecipeHandler(repo),
        delete_recipe=DeleteRecipeHandler(repo),
        add_ingredient=AddIngredientHandler(repo),
        update_ingredient=UpdateIngredientHandler(repo),
        delete_ingredient=DeleteIngredientHandler(repo),
        add_step=AddStepHandler(repo),
        update_step=UpdateStepHandler(repo),
        delete_step=DeleteStepHandler(repo),
        upload_image=UploadImageHandler(repo, storage, queue),
        set_primary_image=SetPrimaryImageHandler(repo),
        delete_image=DeleteImageHandler(repo, queue),
    ).router
    app = FastAPI()
    register_problem_handlers(app)
    app.include_router(router)
    return TestClient(app)
