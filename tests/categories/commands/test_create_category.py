import pytest

from culinary_blog.categories.commands.create_category import CreateCategoryCommand, CreateCategoryHandler
from culinary_blog.errors import ConflictError, ForbiddenError
from tests.categories.fakes import ADMIN, AUTHOR, FakeCategoryRepository


def make_handler():
    repo = FakeCategoryRepository()
    return repo, CreateCategoryHandler(repo)


@pytest.mark.anyio
async def test_admin_creates_category_with_generated_slug():
    repo, handler = make_handler()
    out = await handler.handle(CreateCategoryCommand(ADMIN, "Món Chính", "Mains", "https://x/y.png"))

    assert out.slug == "mon-chinh" and out.name == "Món Chính" and out.recipe_count == 0
    (stored,) = repo.categories.values()
    assert stored.description == "Mains" and stored.image_url == "https://x/y.png"


@pytest.mark.anyio
async def test_slug_clash_gets_numeric_suffix():
    _, handler = make_handler()
    first = await handler.handle(CreateCategoryCommand(ADMIN, "Main Course"))
    second = await handler.handle(CreateCategoryCommand(ADMIN, "Main-Course"))
    third = await handler.handle(CreateCategoryCommand(ADMIN, "Main  Course!"))

    assert [first.slug, second.slug, third.slug] == ["main-course", "main-course-2", "main-course-3"]


@pytest.mark.anyio
async def test_unsluggable_name_falls_back_to_category():
    _, handler = make_handler()
    assert (await handler.handle(CreateCategoryCommand(ADMIN, "!!"))).slug == "category"


@pytest.mark.anyio
async def test_duplicate_name_conflicts():
    _, handler = make_handler()
    await handler.handle(CreateCategoryCommand(ADMIN, "Desserts"))

    with pytest.raises(ConflictError):
        await handler.handle(CreateCategoryCommand(ADMIN, "Desserts"))


@pytest.mark.anyio
async def test_non_admin_is_forbidden_and_nothing_is_written():
    repo, handler = make_handler()

    with pytest.raises(ForbiddenError):
        await handler.handle(CreateCategoryCommand(AUTHOR, "Desserts"))
    assert not repo.categories
