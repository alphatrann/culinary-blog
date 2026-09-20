from datetime import timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from culinary_blog.auth.dependencies import Authenticator
from culinary_blog.auth.security import TokenService
from culinary_blog.problem_details import register_problem_handlers
from culinary_blog.recipes.commands.create_recipe import CreateRecipeHandler
from culinary_blog.recipes.router import RecipeRouter
from tests.recipes.fakes import ADMIN, AUTHOR, READER, FakeRecipeRepository

BASE = "/api/v1/recipes"
TOKENS = TokenService("test-secret-key-at-least-32-bytes-long", timedelta(minutes=15), timedelta(days=7))


def as_user(client: TestClient, principal) -> None:
    client.cookies.set("access_token", TOKENS.create_access_token(principal.user_id, list(principal.roles)))


@pytest.fixture
def repo() -> FakeRecipeRepository:
    return FakeRecipeRepository()


@pytest.fixture
def category_id(repo) -> str:
    return str(repo.add_category())


@pytest.fixture
def client(repo) -> TestClient:
    router = RecipeRouter(authenticator=Authenticator(TOKENS), create_recipe=CreateRecipeHandler(repo)).router
    app = FastAPI()
    register_problem_handlers(app)
    app.include_router(router)
    return TestClient(app)


def payload(category_id: str, /, **overrides) -> dict:
    return {
        "title": "Phở Bò Hà Nội",
        "description": "Traditional beef noodle soup",
        "category_id": category_id,
        "prep_time_minutes": 30,
        "cook_time_minutes": 180,
        "servings": 4,
    } | overrides


def assert_problem(response, status: int) -> None:
    assert response.status_code == status
    assert response.headers["content-type"].startswith("application/problem+json")


# --- create: happy paths --------------------------------------------------------------------------------------------


def test_author_creates_draft_recipe_201_with_location_header(client, category_id):
    as_user(client, AUTHOR)
    response = client.post(BASE, json=payload(category_id))

    assert response.status_code == 201
    assert response.headers["location"] == f"{BASE}/pho-bo-ha-noi"
    body = response.json()
    assert body["slug"] == "pho-bo-ha-noi" and body["status"] == 0 and body["published_at"] is None
    assert body["author_id"] == str(AUTHOR.user_id) and body["category_id"] == category_id
    assert body["difficulty"] == 1 and body["row_version"] == 0
    assert body["steps"] == [] and body["ingredients"] == []
    assert set(body["nutrition"]) == {"calories", "protein", "carbohydrates", "fat", "fiber", "sodium"}


def test_admin_creates_recipe_with_nested_steps_ingredients_and_nutrition(client, category_id):
    as_user(client, ADMIN)
    response = client.post(
        BASE,
        json=payload(
            category_id,
            difficulty=3,
            nutrition={"calories": 450.5, "protein": 30},
            steps=[
                {"title": "Boil", "description": "Boil bones", "duration_minutes": 60},
                {"title": "Serve", "description": "Ladle into bowls"},
            ],
            ingredients=[{"name": "Rice noodles", "quantity": 500, "unit": "gram"}, {"name": "Salt"}],
        ),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["difficulty"] == 3 and body["nutrition"]["calories"] == 450.5
    assert [(s["step_number"], s["title"]) for s in body["steps"]] == [(1, "Boil"), (2, "Serve")]
    assert [(i["name"], i["quantity"], i["unit"]) for i in body["ingredients"]] == [
        ("Rice noodles", 500, "gram"),
        ("Salt", None, None),
    ]


def test_same_title_twice_gets_suffixed_slug(client, category_id):
    as_user(client, AUTHOR)
    client.post(BASE, json=payload(category_id))
    response = client.post(BASE, json=payload(category_id))

    assert response.status_code == 201 and response.json()["slug"] == "pho-bo-ha-noi-2"


# --- create: auth ---------------------------------------------------------------------------------------------------


def test_create_without_cookie_is_401(client, category_id):
    assert_problem(client.post(BASE, json=payload(category_id)), 401)


def test_create_with_invalid_cookie_is_401(client, category_id):
    client.cookies.set("access_token", "not-a-jwt")

    assert_problem(client.post(BASE, json=payload(category_id)), 401)


def test_create_without_author_or_admin_role_is_403(client, repo, category_id):
    as_user(client, READER)
    response = client.post(BASE, json=payload(category_id))

    assert_problem(response, 403)
    assert not repo.recipes


# --- create: validation / errors ------------------------------------------------------------------------------------


def test_unknown_category_is_422_problem_json(client, repo):
    as_user(client, AUTHOR)
    response = client.post(BASE, json=payload("00000000-0000-4000-8000-000000000000"))

    assert_problem(response, 422)
    assert "Category" in response.json()["detail"]
    assert not repo.recipes


@pytest.mark.parametrize(
    "overrides",
    [
        {"title": "Pho"},  # < 5 chars
        {"title": "    x    "},  # < 5 chars once trimmed
        {"title": "x" * 201},
        {"title": "<script>alert(1)</script>"},
        {"description": "   "},
        {"prep_time_minutes": 0},
        {"cook_time_minutes": -5},
        {"servings": 0},
        {"difficulty": 9},
        {"category_id": "not-a-uuid"},
        {"nutrition": {"calories": -1}},
        {"steps": [{"title": "", "description": "x"}]},
        {"steps": [{"title": "Boil", "description": ""}]},
        {"steps": [{"title": "Boil", "description": "x" * 2001}]},
        {"ingredients": [{"name": "Salt", "quantity": 1}]},  # quantity without unit
        {"ingredients": [{"name": "Salt", "unit": "g"}]},  # unit without quantity
        {"ingredients": [{"name": "Salt", "quantity": 0, "unit": "g"}]},
        {"ingredients": [{"name": "x" * 101}]},
    ],
)
def test_invalid_payload_is_422_problem_json(client, repo, category_id, overrides):
    as_user(client, AUTHOR)

    assert_problem(client.post(BASE, json=payload(category_id, **overrides)), 422)
    assert not repo.recipes


def test_missing_required_field_is_422(client, category_id):
    as_user(client, AUTHOR)
    body = payload(category_id)
    del body["servings"]

    assert_problem(client.post(BASE, json=body), 422)


def test_client_supplied_step_number_and_status_are_ignored(client, category_id):
    as_user(client, AUTHOR)
    response = client.post(
        BASE,
        json=payload(category_id, status=1, steps=[{"title": "Boil", "description": "x", "step_number": 9}]),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == 0 and body["steps"][0]["step_number"] == 1
