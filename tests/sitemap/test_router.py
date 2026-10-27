from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient

from culinary_blog.problem_details import register_problem_handlers
from culinary_blog.sitemap.builder import STORED_KEY
from culinary_blog.sitemap.queries.get_sitemap import GetSitemapHandler
from culinary_blog.sitemap.router import SitemapRouter
from tests.recipes.fakes import FakeStorage
from tests.sitemap.fakes import SITE, FakeCategoryRepository, FakeRecipeRepository


def make_client(recipes: FakeRecipeRepository, storage: FakeStorage) -> TestClient:
    handler = GetSitemapHandler(recipes, FakeCategoryRepository(), storage, SITE)
    app = FastAPI()
    register_problem_handlers(app)
    app.include_router(SitemapRouter(handler).router)
    return TestClient(app, raise_server_exceptions=False)


def test_serves_xml_listing_published_recipe_slug():
    recipes = FakeRecipeRepository()
    recipes.published = [("pho-bo-hue", datetime(2026, 10, 1, tzinfo=UTC))]

    response = make_client(recipes, FakeStorage()).get("/sitemap.xml")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/xml")
    assert f"{SITE}/recipes/pho-bo-hue" in response.text


def test_stored_copy_from_worker_is_served_verbatim():
    storage = FakeStorage()
    storage.objects[f"http://storage/{STORED_KEY}"] = b"<urlset>stored</urlset>"

    response = make_client(FakeRecipeRepository(), storage).get("/sitemap.xml")

    assert response.status_code == 200
    assert response.content == b"<urlset>stored</urlset>"


def test_error_case_database_failure_returns_problem_json_500():
    recipes = FakeRecipeRepository()
    recipes.fail = True

    response = make_client(recipes, FakeStorage()).get("/sitemap.xml")

    # No stored copy and no database: the handler raises, the generic handler answers with problem+json, never an
    # empty 200 that crawlers would read as "no pages".
    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/problem+json")
