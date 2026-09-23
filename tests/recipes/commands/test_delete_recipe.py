import uuid

import pytest

from culinary_blog.errors import ForbiddenError, NotFoundError
from culinary_blog.recipes.commands.delete_recipe import DeleteRecipeCommand, DeleteRecipeHandler
from culinary_blog.recipes.enums import RecipeStatus
from culinary_blog.recipes.models import RecipeImage, RecipeIngredient, RecipeStep
from tests.recipes.fakes import ADMIN, AUTHOR, OTHER_AUTHOR, READER, FakeRecipeRepository


def recipe_with_children(repo: FakeRecipeRepository):
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED)
    repo.steps.append(RecipeStep(recipe_id=recipe.id, step_number=1, title="t", description="d"))
    repo.ingredients.append(RecipeIngredient(recipe_id=recipe.id, name="x", order_index=0))
    repo.images.append(RecipeImage(recipe_id=recipe.id, original_url="http://storage/x.jpg", order_index=0))
    return recipe


@pytest.mark.anyio
async def test_delete_soft_deletes_the_recipe_and_bumps_row_version():
    repo = FakeRecipeRepository()
    recipe = recipe_with_children(repo)

    await DeleteRecipeHandler(repo).handle(DeleteRecipeCommand(AUTHOR, recipe.id))

    assert recipe.is_deleted is True
    assert recipe.row_version == 1


@pytest.mark.anyio
async def test_delete_cascades_to_steps_ingredients_and_images():
    repo = FakeRecipeRepository()
    recipe = recipe_with_children(repo)

    await DeleteRecipeHandler(repo).handle(DeleteRecipeCommand(AUTHOR, recipe.id))

    assert all(s.is_deleted for s in repo.steps if s.recipe_id == recipe.id)
    assert all(i.is_deleted for i in repo.ingredients if i.recipe_id == recipe.id)
    assert all(i.is_deleted for i in repo.images if i.recipe_id == recipe.id)


@pytest.mark.anyio
async def test_deleted_recipe_no_longer_visible():
    repo = FakeRecipeRepository()
    recipe = recipe_with_children(repo)

    await DeleteRecipeHandler(repo).handle(DeleteRecipeCommand(AUTHOR, recipe.id))

    assert await repo.get_by_id(recipe.id) is None


@pytest.mark.anyio
async def test_admin_can_delete_any_recipe():
    repo = FakeRecipeRepository()
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED)

    await DeleteRecipeHandler(repo).handle(DeleteRecipeCommand(ADMIN, recipe.id))

    assert recipe.is_deleted is True


@pytest.mark.anyio
@pytest.mark.parametrize("actor", [OTHER_AUTHOR, READER])
async def test_forbidden_for_non_owner(actor):
    repo = FakeRecipeRepository()
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED)

    with pytest.raises(ForbiddenError):
        await DeleteRecipeHandler(repo).handle(DeleteRecipeCommand(actor, recipe.id))
    assert recipe.is_deleted is False


@pytest.mark.anyio
async def test_unknown_recipe_is_not_found():
    repo = FakeRecipeRepository()
    with pytest.raises(NotFoundError):
        await DeleteRecipeHandler(repo).handle(DeleteRecipeCommand(AUTHOR, uuid.uuid4()))


@pytest.mark.anyio
async def test_already_deleted_recipe_is_not_found():
    repo = FakeRecipeRepository()
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED)
    handler = DeleteRecipeHandler(repo)
    await handler.handle(DeleteRecipeCommand(AUTHOR, recipe.id))

    with pytest.raises(NotFoundError):
        await handler.handle(DeleteRecipeCommand(AUTHOR, recipe.id))
