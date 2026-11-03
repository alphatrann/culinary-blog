from datetime import UTC, datetime
from xml.etree import ElementTree

import pytest

from culinary_blog.errors import ServiceUnavailableError
from culinary_blog.sitemap.builder import SITEMAP_NS, STORED_KEY
from culinary_blog.sitemap.queries.get_sitemap import GetSitemapHandler, GetSitemapQuery
from tests.recipes.fakes import FakeStorage
from tests.sitemap.fakes import SITE, FakeCategoryRepository, FakeRecipeRepository

WHEN = datetime(2026, 10, 1, tzinfo=UTC)


@pytest.fixture
def recipes() -> FakeRecipeRepository:
    return FakeRecipeRepository()


@pytest.fixture
def categories() -> FakeCategoryRepository:
    return FakeCategoryRepository()


@pytest.fixture
def storage() -> FakeStorage:
    return FakeStorage()


@pytest.fixture
def handler(recipes, categories, storage) -> GetSitemapHandler:
    return GetSitemapHandler(recipes, categories, storage, SITE)


def locs(xml: bytes) -> list[str]:
    return [node.text for node in ElementTree.fromstring(xml).iter(f"{{{SITEMAP_NS}}}loc")]


@pytest.mark.anyio
async def test_builds_from_database_when_nothing_is_stored(handler, recipes, categories):
    recipes.published = [("pho-bo", WHEN)]
    categories.live = [("mon-chinh", WHEN)]

    assert locs(await handler.handle(GetSitemapQuery())) == [
        f"{SITE}/",
        f"{SITE}/categories",
        f"{SITE}/recipes/pho-bo",
        f"{SITE}/categories/mon-chinh",
    ]


@pytest.mark.anyio
async def test_serves_stored_copy_without_querying(handler, recipes, storage):
    storage.objects[f"http://storage/{STORED_KEY}"] = b"<urlset/>"
    recipes.fail = True  # would raise if the handler touched the database

    assert await handler.handle(GetSitemapQuery()) == b"<urlset/>"


@pytest.mark.anyio
async def test_storage_outage_falls_back_to_a_fresh_build(handler, recipes, storage):
    async def down(key: str) -> bytes | None:
        raise ServiceUnavailableError()

    storage.get_at = down  # type: ignore[method-assign]
    recipes.published = [("pho-bo", WHEN)]

    assert f"{SITE}/recipes/pho-bo" in locs(await handler.handle(GetSitemapQuery()))


@pytest.mark.anyio
async def test_database_failure_without_stored_copy_propagates(handler, recipes):
    recipes.fail = True

    with pytest.raises(RuntimeError):
        await handler.handle(GetSitemapQuery())
