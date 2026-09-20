import uuid

import pytest

from culinary_blog.categories.commands.update_category import UpdateCategoryCommand, UpdateCategoryHandler
from culinary_blog.errors import ConflictError, ForbiddenError, NotFoundError
from culinary_blog.recipes.enums import RecipeStatus
from tests.categories.fakes import ADMIN, AUTHOR, FakeCategoryRepository, make_category


def setup():
    repo = FakeCategoryRepository()
    return repo, make_category(repo, "Main", "main"), UpdateCategoryHandler(repo)


@pytest.mark.anyio
async def test_update_changes_fields_but_never_the_slug():
    repo, category, handler = setup()
    repo.add_recipe(category, AUTHOR, RecipeStatus.PUBLISHED)

    out = await handler.handle(UpdateCategoryCommand(ADMIN, category.id, "Entrées", "New", "https://x/i.png", 3))

    assert (out.name, out.slug, out.description, out.image_url) == ("Entrées", "main", "New", "https://x/i.png")
    assert out.recipe_count == 1
    assert category.order_index == 3 and category.row_version == 1


@pytest.mark.anyio
async def test_update_keeping_own_name_is_not_a_conflict():
    _, category, handler = setup()
    out = await handler.handle(UpdateCategoryCommand(ADMIN, category.id, "Main", "d", None, 0))
    assert out.name == "Main"


@pytest.mark.anyio
async def test_update_to_another_categorys_name_conflicts():
    repo, category, handler = setup()
    make_category(repo, "Desserts", "desserts")

    with pytest.raises(ConflictError):
        await handler.handle(UpdateCategoryCommand(ADMIN, category.id, "Desserts", None, None, 0))


@pytest.mark.anyio
async def test_unknown_id_is_not_found():
    _, _, handler = setup()
    with pytest.raises(NotFoundError):
        await handler.handle(UpdateCategoryCommand(ADMIN, uuid.uuid4(), "X Y", None, None, 0))


@pytest.mark.anyio
async def test_non_admin_is_forbidden_and_category_untouched():
    _, category, handler = setup()

    with pytest.raises(ForbiddenError):
        await handler.handle(UpdateCategoryCommand(AUTHOR, category.id, "Hacked", None, None, 0))
    assert category.name == "Main"
