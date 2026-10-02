"""M6b: cache-aside on the category read handlers and invalidation from the category write handlers."""

import pytest

from culinary_blog.cache import keys
from culinary_blog.categories.commands.create_category import CreateCategoryCommand, CreateCategoryHandler
from culinary_blog.categories.commands.update_category import UpdateCategoryCommand, UpdateCategoryHandler
from culinary_blog.categories.queries.get_category import GetCategoryHandler, GetCategoryQuery
from culinary_blog.categories.queries.list_categories import ListCategoriesHandler, ListCategoriesQuery
from culinary_blog.errors import ForbiddenError, NotFoundError
from culinary_blog.recipes.enums import RecipeStatus
from tests.cache.fakes import FakeCache
from tests.categories.fakes import ADMIN, AUTHOR, FakeCategoryRepository, invalidator, make_category


@pytest.fixture
def repo() -> FakeCategoryRepository:
    return FakeCategoryRepository()


@pytest.fixture
def cache() -> FakeCache:
    return FakeCache()


@pytest.mark.anyio
async def test_category_list_is_cached_under_one_key_with_the_hour_ttl(repo, cache):
    make_category(repo, "Main", "main")
    handler = ListCategoriesHandler(repo, cache)

    first = await handler.handle(ListCategoriesQuery())
    make_category(repo, "Soups", "soups")
    second = await handler.handle(ListCategoriesQuery())

    assert first == second and len(second) == 1
    assert cache.loads == 1
    assert cache.store[keys.CATEGORIES_ALL][1] == 3600


@pytest.mark.anyio
async def test_guest_category_page_is_cached_per_page_and_signed_in_viewers_bypass(repo, cache):
    category = make_category(repo, "Main", "main")
    repo.add_recipe(category, AUTHOR, RecipeStatus.DRAFT, title="Draft")
    handler = GetCategoryHandler(repo, cache)

    guest = await handler.handle(GetCategoryQuery("main", 1, 12))
    await handler.handle(GetCategoryQuery("main", 1, 12))
    await handler.handle(GetCategoryQuery("main", 2, 12))
    mine = await handler.handle(GetCategoryQuery("main", 1, 12, viewer=AUTHOR))

    assert guest.recipes.items == [] and [r.title for r in mine.recipes.items] == ["Draft"]
    assert cache.loads == 2  # page 1 and page 2; the signed-in read never touched the cache
    assert len(cache.store) == 2


@pytest.mark.anyio
async def test_unknown_category_is_not_cached(repo, cache):
    with pytest.raises(NotFoundError):
        await GetCategoryHandler(repo, cache).handle(GetCategoryQuery("nope", 1, 12))

    assert cache.store == {}


@pytest.mark.anyio
async def test_reads_still_work_when_the_cache_is_down(repo):
    make_category(repo, "Main", "main")
    cache = FakeCache(unavailable=True)

    assert len(await ListCategoriesHandler(repo, cache).handle(ListCategoriesQuery())) == 1
    assert (await GetCategoryHandler(repo, cache).handle(GetCategoryQuery("main", 1, 12))).category.slug == "main"


@pytest.mark.anyio
async def test_create_drops_the_list(repo, cache):
    await CreateCategoryHandler(repo, invalidator(cache)).handle(CreateCategoryCommand(ADMIN, "Desserts"))

    assert cache.deleted == [keys.CATEGORIES_ALL] and cache.generation == 0


@pytest.mark.anyio
async def test_update_drops_the_list_and_bumps_category_pages(repo, cache):
    category = make_category(repo, "Main", "main")

    await UpdateCategoryHandler(repo, invalidator(cache)).handle(
        UpdateCategoryCommand(ADMIN, category.id, "Entrées", None, None, 0)
    )

    assert cache.deleted == [keys.CATEGORIES_ALL] and cache.generation == 1


@pytest.mark.anyio
async def test_a_rename_shows_up_immediately_in_a_warm_list(repo, cache):
    category = make_category(repo, "Main", "main")
    lists = ListCategoriesHandler(repo, cache)
    await lists.handle(ListCategoriesQuery())

    await UpdateCategoryHandler(repo, invalidator(cache)).handle(
        UpdateCategoryCommand(ADMIN, category.id, "Entrées", None, None, 0)
    )

    assert [c.name for c in await lists.handle(ListCategoriesQuery())] == ["Entrées"]


@pytest.mark.anyio
async def test_rejected_writes_do_not_invalidate(repo, cache):
    with pytest.raises(ForbiddenError):
        await CreateCategoryHandler(repo, invalidator(cache)).handle(CreateCategoryCommand(AUTHOR, "Desserts"))

    assert cache.deleted == [] and cache.generation == 0
