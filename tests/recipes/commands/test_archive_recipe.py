import uuid

import pytest

from culinary_blog.errors import ForbiddenError, NotFoundError
from culinary_blog.recipes.commands.archive_recipe import ArchiveRecipeCommand, ArchiveRecipeHandler
from culinary_blog.recipes.commands.unarchive_recipe import UnarchiveRecipeCommand, UnarchiveRecipeHandler
from culinary_blog.recipes.enums import RecipeStatus
from tests.recipes.fakes import ADMIN, AUTHOR, OTHER_AUTHOR, READER, FakeRecipeRepository, invalidator


@pytest.mark.anyio
@pytest.mark.parametrize("actor", [AUTHOR, ADMIN])
async def test_owner_and_admin_archive(actor):
    repo = FakeRecipeRepository()
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED)
    out = await ArchiveRecipeHandler(repo, invalidator()).handle(ArchiveRecipeCommand(actor, recipe.id))

    assert out.status == RecipeStatus.ARCHIVED and recipe.is_deleted is False


@pytest.mark.anyio
async def test_archive_is_idempotent():
    repo = FakeRecipeRepository()
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.ARCHIVED)
    out = await ArchiveRecipeHandler(repo, invalidator()).handle(ArchiveRecipeCommand(AUTHOR, recipe.id))

    assert out.row_version == recipe.row_version == 0


@pytest.mark.anyio
@pytest.mark.parametrize("actor", [OTHER_AUTHOR, READER])
async def test_archive_forbidden(actor):
    repo = FakeRecipeRepository()
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED)
    with pytest.raises(ForbiddenError):
        await ArchiveRecipeHandler(repo, invalidator()).handle(ArchiveRecipeCommand(actor, recipe.id))


@pytest.mark.anyio
async def test_archive_unknown_is_not_found():
    with pytest.raises(NotFoundError):
        await ArchiveRecipeHandler(FakeRecipeRepository(), invalidator()).handle(
            ArchiveRecipeCommand(AUTHOR, uuid.uuid4())
        )


@pytest.mark.anyio
async def test_unarchive_restores_as_draft():
    repo = FakeRecipeRepository()
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.ARCHIVED)
    out = await UnarchiveRecipeHandler(repo, invalidator()).handle(UnarchiveRecipeCommand(AUTHOR, recipe.id))

    assert out.status == RecipeStatus.DRAFT


@pytest.mark.anyio
async def test_unarchive_leaves_non_archived_recipes_alone():
    repo = FakeRecipeRepository()
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED)
    out = await UnarchiveRecipeHandler(repo, invalidator()).handle(UnarchiveRecipeCommand(AUTHOR, recipe.id))

    assert out.status == RecipeStatus.PUBLISHED


@pytest.mark.anyio
async def test_unarchive_forbidden_for_other_author():
    repo = FakeRecipeRepository()
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.ARCHIVED)
    with pytest.raises(ForbiddenError):
        await UnarchiveRecipeHandler(repo, invalidator()).handle(UnarchiveRecipeCommand(OTHER_AUTHOR, recipe.id))
