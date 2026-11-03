import uuid

import pytest

from culinary_blog.errors import ForbiddenError, NotFoundError
from culinary_blog.recipes.enums import RecipeStatus
from culinary_blog.recipes.queries.get_recipe_for_edit import GetRecipeForEditHandler, GetRecipeForEditQuery
from tests.recipes.fakes import ADMIN, AUTHOR, OTHER_AUTHOR, READER, FakeRecipeRepository


def make_handler():
    repo = FakeRecipeRepository()
    return repo, GetRecipeForEditHandler(repo)


@pytest.mark.anyio
async def test_owner_reads_their_draft_by_id():
    repo, handler = make_handler()
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT, category_id=repo.add_category())

    out = await handler.handle(GetRecipeForEditQuery(recipe.id, AUTHOR))

    assert out.id == recipe.id and out.status == RecipeStatus.DRAFT


@pytest.mark.anyio
async def test_admin_reads_any_draft_by_id():
    repo, handler = make_handler()
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT, category_id=repo.add_category())

    out = await handler.handle(GetRecipeForEditQuery(recipe.id, ADMIN))

    assert out.id == recipe.id


@pytest.mark.anyio
@pytest.mark.parametrize("actor", [OTHER_AUTHOR, READER])
async def test_non_owner_is_forbidden_even_for_published_recipes(actor):
    repo, handler = make_handler()
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED, category_id=repo.add_category())

    with pytest.raises(ForbiddenError):
        await handler.handle(GetRecipeForEditQuery(recipe.id, actor))


@pytest.mark.anyio
async def test_unknown_id_is_not_found():
    _, handler = make_handler()

    with pytest.raises(NotFoundError):
        await handler.handle(GetRecipeForEditQuery(uuid.uuid4(), AUTHOR))
