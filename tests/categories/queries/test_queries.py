import pytest

from culinary_blog.categories.queries.get_category import GetCategoryHandler, GetCategoryQuery
from culinary_blog.categories.queries.list_categories import ListCategoriesHandler, ListCategoriesQuery
from culinary_blog.errors import NotFoundError
from culinary_blog.recipes.enums import RecipeStatus
from tests.categories.fakes import ADMIN, AUTHOR, OTHER_AUTHOR, FakeCategoryRepository, make_category


@pytest.mark.anyio
async def test_list_is_empty_when_no_categories():
    assert await ListCategoriesHandler(FakeCategoryRepository()).handle(ListCategoriesQuery()) == []


@pytest.mark.anyio
async def test_list_is_sorted_by_name_and_counts_only_published():
    repo = FakeCategoryRepository()
    zed = make_category(repo, "Zed", "zed")
    alpha = make_category(repo, "Alpha", "alpha")
    repo.add_recipe(alpha, AUTHOR, RecipeStatus.PUBLISHED)
    repo.add_recipe(alpha, AUTHOR, RecipeStatus.PUBLISHED)
    repo.add_recipe(alpha, AUTHOR, RecipeStatus.DRAFT)
    repo.add_recipe(zed, AUTHOR, RecipeStatus.ARCHIVED)
    make_category(repo, "Gone", "gone", is_deleted=True)

    out = await ListCategoriesHandler(repo).handle(ListCategoriesQuery())

    assert [(c.name, c.recipe_count) for c in out] == [("Alpha", 2), ("Zed", 0)]


def detail_setup():
    repo = FakeCategoryRepository()
    category = make_category(repo, "Main", "main")
    published = repo.add_recipe(category, OTHER_AUTHOR, RecipeStatus.PUBLISHED, "Pub")
    own_draft = repo.add_recipe(category, AUTHOR, RecipeStatus.DRAFT, "Mine")
    other_draft = repo.add_recipe(category, OTHER_AUTHOR, RecipeStatus.DRAFT, "Theirs")
    return GetCategoryHandler(repo), published, own_draft, other_draft


@pytest.mark.anyio
async def test_guest_sees_only_published():
    handler, published, _, _ = detail_setup()
    out = await handler.handle(GetCategoryQuery("main", 1, 12))

    assert [r.id for r in out.recipes.items] == [published.id]
    assert out.category.recipe_count == 1 and out.recipes.total_count == 1


@pytest.mark.anyio
async def test_author_also_sees_own_non_published():
    handler, published, own_draft, _ = detail_setup()
    out = await handler.handle(GetCategoryQuery("main", 1, 12, AUTHOR))

    assert {r.id for r in out.recipes.items} == {published.id, own_draft.id}


@pytest.mark.anyio
async def test_admin_sees_everything():
    handler, *_ = detail_setup()
    out = await handler.handle(GetCategoryQuery("main", 1, 12, ADMIN))
    assert out.recipes.total_count == 3


@pytest.mark.anyio
async def test_pagination_metadata():
    repo = FakeCategoryRepository()
    category = make_category(repo, "Main", "main")
    for i in range(5):
        repo.add_recipe(category, AUTHOR, RecipeStatus.PUBLISHED, f"R{i}")

    out = await GetCategoryHandler(repo).handle(GetCategoryQuery("main", 3, 2))

    assert (out.recipes.page, out.recipes.page_size, out.recipes.total_count, out.recipes.total_pages) == (3, 2, 5, 3)
    assert len(out.recipes.items) == 1


@pytest.mark.anyio
async def test_page_past_the_end_is_empty_not_an_error():
    handler, *_ = detail_setup()
    out = await handler.handle(GetCategoryQuery("main", 9, 12))
    assert out.recipes.items == [] and out.recipes.total_pages == 1


@pytest.mark.anyio
async def test_unknown_slug_is_not_found():
    with pytest.raises(NotFoundError):
        await GetCategoryHandler(FakeCategoryRepository()).handle(GetCategoryQuery("nope", 1, 12))
