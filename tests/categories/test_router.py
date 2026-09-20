import uuid
from datetime import timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from culinary_blog.auth.dependencies import Authenticator
from culinary_blog.auth.security import TokenService
from culinary_blog.categories.commands.create_category import CreateCategoryHandler
from culinary_blog.categories.commands.update_category import UpdateCategoryHandler
from culinary_blog.categories.queries.get_category import GetCategoryHandler
from culinary_blog.categories.queries.list_categories import ListCategoriesHandler
from culinary_blog.categories.router import CategoryRouter
from culinary_blog.problem_details import register_problem_handlers
from culinary_blog.recipes.enums import RecipeStatus
from tests.categories.fakes import ADMIN, AUTHOR, FakeCategoryRepository, make_category

BASE = "/api/v1/categories"
TOKENS = TokenService("test-secret-key-at-least-32-bytes-long", timedelta(minutes=15), timedelta(days=7))


def as_user(client: TestClient, principal) -> None:
    client.cookies.set("access_token", TOKENS.create_access_token(principal.user_id, list(principal.roles)))


@pytest.fixture
def repo() -> FakeCategoryRepository:
    return FakeCategoryRepository()


@pytest.fixture
def client(repo) -> TestClient:
    router = CategoryRouter(
        authenticator=Authenticator(TOKENS),
        create_category=CreateCategoryHandler(repo),
        update_category=UpdateCategoryHandler(repo),
        list_categories=ListCategoriesHandler(repo),
        get_category=GetCategoryHandler(repo),
    ).router
    app = FastAPI()
    register_problem_handlers(app)
    app.include_router(router)
    return TestClient(app)


# --- create ---------------------------------------------------------------------------------------------------------


def test_admin_creates_category_201_with_location_header(client):
    as_user(client, ADMIN)
    response = client.post(BASE, json={"name": "Món Chính", "description": "Mains"})

    assert response.status_code == 201
    assert response.headers["location"] == f"{BASE}/mon-chinh"
    body = response.json()
    assert body["slug"] == "mon-chinh" and body["recipe_count"] == 0
    assert set(body) == {"id", "name", "slug", "description", "image_url", "recipe_count"}


def test_create_duplicate_name_is_409_problem_json(client):
    as_user(client, ADMIN)
    client.post(BASE, json={"name": "Desserts"})
    response = client.post(BASE, json={"name": "Desserts"})

    assert response.status_code == 409
    assert response.headers["content-type"].startswith("application/problem+json")


def test_create_without_cookie_is_401(client):
    assert client.post(BASE, json={"name": "Desserts"}).status_code == 401


def test_create_as_author_is_403(client):
    as_user(client, AUTHOR)
    response = client.post(BASE, json={"name": "Desserts"})

    assert response.status_code == 403
    assert response.headers["content-type"].startswith("application/problem+json")


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"name": "x"},
        {"name": "a" * 51},
        {"name": "<b>Bold</b>"},
        {"name": "   "},
    ],
)
def test_create_invalid_body_is_422(client, body):
    as_user(client, ADMIN)
    response = client.post(BASE, json=body)
    assert response.status_code == 422 and response.headers["content-type"].startswith("application/problem+json")


def test_update_negative_order_index_is_422(client, repo):
    category = make_category(repo)
    as_user(client, ADMIN)
    assert client.put(f"{BASE}/{category.id}", json={"name": "Ok", "order_index": -1}).status_code == 422


# --- update ---------------------------------------------------------------------------------------------------------


def test_admin_updates_category_and_slug_is_stable(client, repo):
    category = make_category(repo, "Main", "main")
    as_user(client, ADMIN)
    response = client.put(f"{BASE}/{category.id}", json={"name": "Entrées", "description": "d", "order_index": 2})

    assert response.status_code == 200
    assert response.json()["name"] == "Entrées" and response.json()["slug"] == "main"


def test_update_unknown_id_is_404(client):
    as_user(client, ADMIN)
    assert client.put(f"{BASE}/{uuid.uuid4()}", json={"name": "Whatever"}).status_code == 404


def test_update_as_author_is_403(client, repo):
    category = make_category(repo)
    as_user(client, AUTHOR)
    assert client.put(f"{BASE}/{category.id}", json={"name": "Whatever"}).status_code == 403


def test_update_without_cookie_is_401(client, repo):
    category = make_category(repo)
    assert client.put(f"{BASE}/{category.id}", json={"name": "Whatever"}).status_code == 401


def test_update_bad_uuid_is_422(client):
    as_user(client, ADMIN)
    assert client.put(f"{BASE}/not-a-uuid", json={"name": "Whatever"}).status_code == 422


# --- list / detail (public) -----------------------------------------------------------------------------------------


def test_list_is_public_and_empty_array_when_none(client):
    response = client.get(BASE)
    assert response.status_code == 200 and response.json() == []


def test_list_returns_categories_with_published_counts(client, repo):
    category = make_category(repo, "Main", "main")
    repo.add_recipe(category, AUTHOR, RecipeStatus.PUBLISHED)
    repo.add_recipe(category, AUTHOR, RecipeStatus.DRAFT)

    (item,) = client.get(BASE).json()
    assert item["slug"] == "main" and item["recipe_count"] == 1


def test_detail_returns_category_and_page_of_published_recipes(client, repo):
    category = make_category(repo, "Main", "main")
    repo.add_recipe(category, AUTHOR, RecipeStatus.PUBLISHED, "Pho")
    repo.add_recipe(category, AUTHOR, RecipeStatus.DRAFT, "Secret")

    response = client.get(f"{BASE}/main")

    assert response.status_code == 200
    body = response.json()
    assert body["category"]["slug"] == "main"
    assert [r["title"] for r in body["recipes"]["items"]] == ["Pho"]
    assert {k: body["recipes"][k] for k in ("total_count", "page", "page_size", "total_pages")} == {
        "total_count": 1,
        "page": 1,
        "page_size": 12,
        "total_pages": 1,
    }


def test_detail_shows_logged_in_authors_own_draft(client, repo):
    category = make_category(repo, "Main", "main")
    repo.add_recipe(category, AUTHOR, RecipeStatus.DRAFT, "Mine")
    as_user(client, AUTHOR)

    assert [r["title"] for r in client.get(f"{BASE}/main").json()["recipes"]["items"]] == ["Mine"]


def test_detail_with_garbage_cookie_is_treated_as_guest(client, repo):
    category = make_category(repo, "Main", "main")
    repo.add_recipe(category, AUTHOR, RecipeStatus.DRAFT, "Mine")
    client.cookies.set("access_token", "garbage")

    response = client.get(f"{BASE}/main")
    assert response.status_code == 200 and response.json()["recipes"]["items"] == []


def test_detail_unknown_slug_is_404_problem_json(client):
    response = client.get(f"{BASE}/nope")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")


@pytest.mark.parametrize("query", ["page=0", "page_size=0", "page_size=51", "page=abc"])
def test_detail_bad_pagination_is_422(client, repo, query):
    make_category(repo, "Main", "main")
    assert client.get(f"{BASE}/main?{query}").status_code == 422
