import uuid

import pytest

from culinary_blog.categories.commands.delete_category import DeleteCategoryCommand, DeleteCategoryHandler
from culinary_blog.errors import ConflictError, ForbiddenError, NotFoundError
from culinary_blog.recipes.enums import RecipeStatus
from tests.categories.fakes import ADMIN, AUTHOR, FakeCategoryRepository, invalidator, make_category


def setup():
    repo = FakeCategoryRepository()
    return repo, make_category(repo, "Main", "main"), DeleteCategoryHandler(repo, invalidator())


@pytest.mark.anyio
async def test_empty_category_is_soft_deleted():
    repo, category, handler = setup()
    await handler.handle(DeleteCategoryCommand(ADMIN, category.id))

    assert category.is_deleted is True
    assert await repo.get_by_id(category.id) is None


@pytest.mark.anyio
@pytest.mark.parametrize("status", [RecipeStatus.DRAFT, RecipeStatus.PUBLISHED, RecipeStatus.ARCHIVED])
async def test_category_with_recipes_of_any_status_conflicts_with_count(status):
    repo, category, handler = setup()
    repo.add_recipe(category, AUTHOR, status)
    repo.add_recipe(category, AUTHOR, RecipeStatus.DRAFT)

    with pytest.raises(ConflictError, match="2 recipe"):
        await handler.handle(DeleteCategoryCommand(ADMIN, category.id))
    assert category.is_deleted is False


@pytest.mark.anyio
async def test_soft_deleted_recipes_do_not_block():
    repo, category, handler = setup()
    repo.add_recipe(category, AUTHOR, RecipeStatus.DRAFT).is_deleted = True

    await handler.handle(DeleteCategoryCommand(ADMIN, category.id))
    assert category.is_deleted is True


@pytest.mark.anyio
async def test_non_admin_is_forbidden():
    _, category, handler = setup()
    with pytest.raises(ForbiddenError):
        await handler.handle(DeleteCategoryCommand(AUTHOR, category.id))


@pytest.mark.anyio
async def test_unknown_id_is_not_found():
    _, _, handler = setup()
    with pytest.raises(NotFoundError):
        await handler.handle(DeleteCategoryCommand(ADMIN, uuid.uuid4()))
