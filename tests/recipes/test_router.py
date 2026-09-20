from datetime import timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from culinary_blog.auth.dependencies import Authenticator
from culinary_blog.auth.security import TokenService
from culinary_blog.problem_details import register_problem_handlers
from culinary_blog.recipes.commands.create_recipe import CreateRecipeHandler
from culinary_blog.recipes.commands.update_recipe import UpdateRecipeHandler
from culinary_blog.recipes.enums import RecipeDifficulty, RecipeStatus
from culinary_blog.recipes.queries.get_recipe import GetRecipeHandler
from culinary_blog.recipes.queries.list_recipes import ListRecipesHandler
from culinary_blog.recipes.router import RecipeRouter
from tests.recipes.fakes import ADMIN, AUTHOR, OTHER_AUTHOR, READER, FakeRecipeRepository

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
    router = RecipeRouter(
        authenticator=Authenticator(TOKENS),
        create_recipe=CreateRecipeHandler(repo),
        update_recipe=UpdateRecipeHandler(repo),
        list_recipes=ListRecipesHandler(repo),
        get_recipe=GetRecipeHandler(repo),
    ).router
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


def test_create_returns_etag_matching_row_version(client, category_id):
    as_user(client, AUTHOR)
    response = client.post(BASE, json=payload(category_id))

    assert response.headers["etag"] == '"0"'


# --- update ---------------------------------------------------------------------------------------------------------


def update_body(recipe, **overrides) -> dict:
    return payload(str(recipe.category_id), title="Phở Bò Tái", servings=6, difficulty=3) | overrides


@pytest.fixture
def owned(repo):
    return repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED)


def put(client, recipe, body: dict, if_match: str | None = "0"):
    headers = {} if if_match is None else {"If-Match": if_match}
    return client.put(f"{BASE}/{recipe.id}", json=body, headers=headers)


def test_owner_updates_recipe_200_with_new_etag(client, owned):
    as_user(client, AUTHOR)
    response = put(client, owned, update_body(owned))

    assert response.status_code == 200
    body = response.json()
    assert (body["title"], body["servings"], body["difficulty"], body["row_version"]) == ("Phở Bò Tái", 6, 3, 1)
    assert body["slug"] == owned.slug and body["status"] == 1  # slug and status are not editable here
    assert response.headers["etag"] == '"1"'


@pytest.mark.parametrize("header", ["0", '"0"', 'W/"0"', " 0 "])
def test_if_match_accepts_bare_quoted_and_weak_etag_forms(client, owned, header):
    as_user(client, AUTHOR)

    assert put(client, owned, update_body(owned), header).status_code == 200


def test_admin_can_update_any_recipe(client, owned):
    as_user(client, ADMIN)

    assert put(client, owned, update_body(owned)).status_code == 200


def test_stale_if_match_is_409_problem_json_and_nothing_changes(client, repo, owned):
    as_user(client, AUTHOR)
    assert put(client, owned, update_body(owned)).status_code == 200
    response = put(client, owned, update_body(owned, title="Stale overwrite"), "0")

    assert_problem(response, 409)
    assert "thay đổi" in response.json()["detail"]
    assert repo.recipes[owned.id].title == "Phở Bò Tái" and repo.recipes[owned.id].row_version == 1


def test_update_with_fresh_etag_from_previous_response_succeeds(client, owned):
    as_user(client, AUTHOR)
    etag = put(client, owned, update_body(owned)).headers["etag"]
    response = put(client, owned, update_body(owned, title="Second edit"), etag)

    assert response.status_code == 200 and response.json()["row_version"] == 2


def test_update_without_if_match_is_422(client, owned):
    as_user(client, AUTHOR)

    assert_problem(put(client, owned, update_body(owned), None), 422)


@pytest.mark.parametrize("header", ["abc", "", "-1", "1.5", "*"])
def test_update_with_malformed_if_match_is_422(client, owned, header):
    as_user(client, AUTHOR)

    assert_problem(put(client, owned, update_body(owned), header), 422)


def test_update_without_cookie_is_401(client, owned):
    assert_problem(put(client, owned, update_body(owned)), 401)


def test_update_by_another_author_is_403(client, repo, owned):
    as_user(client, OTHER_AUTHOR)

    assert_problem(put(client, owned, update_body(owned)), 403)
    assert repo.recipes[owned.id].row_version == 0


def test_update_unknown_recipe_is_404(client, owned):
    as_user(client, AUTHOR)
    response = client.put(
        f"{BASE}/00000000-0000-4000-8000-000000000000", json=update_body(owned), headers={"If-Match": "0"}
    )

    assert_problem(response, 404)


def test_update_with_malformed_id_is_422(client, owned):
    as_user(client, AUTHOR)

    assert_problem(client.put(f"{BASE}/not-a-uuid", json=update_body(owned), headers={"If-Match": "0"}), 422)


def test_update_with_unknown_category_is_422(client, owned):
    as_user(client, AUTHOR)
    body = update_body(owned, category_id="00000000-0000-4000-8000-000000000000")

    assert_problem(put(client, owned, body), 422)


@pytest.mark.parametrize("overrides", [{"title": "Pho"}, {"servings": 0}, {"difficulty": 9}, {"prep_time_minutes": -1}])
def test_update_with_invalid_payload_is_422(client, repo, owned, overrides):
    as_user(client, AUTHOR)

    assert_problem(put(client, owned, update_body(owned, **overrides)), 422)
    assert repo.recipes[owned.id].row_version == 0


def test_update_ignores_client_supplied_slug_status_and_steps(client, owned):
    as_user(client, AUTHOR)
    body = update_body(owned, slug="hijacked", status=2, steps=[{"title": "x", "description": "y"}])
    response = put(client, owned, body)

    assert response.status_code == 200
    assert response.json()["slug"] == owned.slug and response.json()["status"] == 1 and response.json()["steps"] == []


# --- detail ---------------------------------------------------------------------------------------------------------


def test_guest_gets_published_recipe_detail_with_etag(client, owned):
    response = client.get(f"{BASE}/{owned.slug}")

    assert response.status_code == 200 and response.headers["etag"] == '"0"'
    body = response.json()
    assert body["id"] == str(owned.id) and body["row_version"] == 0
    assert set(body) >= {"steps", "ingredients", "images", "nutrition", "category", "author"}
    assert set(body["author"]) == {"id", "display_name", "avatar_url"}
    assert set(body["category"]) == {"id", "name", "slug"}


def test_detail_unknown_slug_is_404_problem_json(client):
    assert_problem(client.get(f"{BASE}/nope"), 404)


@pytest.mark.parametrize("status", [RecipeStatus.DRAFT, RecipeStatus.ARCHIVED])
def test_unpublished_detail_is_403_for_guest_and_other_author(client, repo, status):
    recipe = repo.seed_recipe(AUTHOR, status)

    assert_problem(client.get(f"{BASE}/{recipe.slug}"), 403)
    as_user(client, OTHER_AUTHOR)
    assert_problem(client.get(f"{BASE}/{recipe.slug}"), 403)


def test_unpublished_detail_is_visible_to_owner_and_admin(client, repo):
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT)
    as_user(client, AUTHOR)
    assert client.get(f"{BASE}/{recipe.slug}").status_code == 200
    as_user(client, ADMIN)
    assert client.get(f"{BASE}/{recipe.slug}").status_code == 200


def test_detail_with_bad_cookie_degrades_to_guest(client, repo):
    published, draft = repo.seed_recipe(AUTHOR), repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT)
    client.cookies.set("access_token", "garbage")

    assert client.get(f"{BASE}/{published.slug}").status_code == 200
    assert client.get(f"{BASE}/{draft.slug}").status_code == 403


def test_detail_after_update_reflects_new_row_version(client, owned):
    as_user(client, AUTHOR)
    put(client, owned, update_body(owned))
    response = client.get(f"{BASE}/{owned.slug}")

    assert response.json()["row_version"] == 1 and response.headers["etag"] == '"1"'


# --- list -----------------------------------------------------------------------------------------------------------


def test_guest_list_shows_only_published_with_page_envelope(client, repo):
    repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED, title="Published")
    repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT, title="Draft")
    response = client.get(BASE)

    assert response.status_code == 200
    body = response.json()
    assert [i["title"] for i in body["items"]] == ["Published"]
    assert (body["total_count"], body["page"], body["page_size"], body["total_pages"]) == (1, 1, 12, 1)
    assert (body["has_next_page"], body["has_previous_page"]) == (False, False)


def test_author_list_includes_own_draft_but_not_others(client, repo):
    repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT, title="Mine")
    repo.seed_recipe(OTHER_AUTHOR, RecipeStatus.DRAFT, title="Theirs")
    as_user(client, AUTHOR)

    assert [i["title"] for i in client.get(BASE).json()["items"]] == ["Mine"]


def test_admin_list_includes_everything(client, repo):
    repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT)
    repo.seed_recipe(OTHER_AUTHOR, RecipeStatus.ARCHIVED)
    as_user(client, ADMIN)

    assert client.get(BASE).json()["total_count"] == 2


def test_list_filters_by_category_difficulty_name_and_max_cook_time(client, repo):
    soups = repo.add_category("Soups")
    easy, hard = RecipeDifficulty.EASY, RecipeDifficulty.HARD
    repo.seed_recipe(AUTHOR, title="Match", category_id=soups, difficulty=easy, cook_time_minutes=20)
    repo.seed_recipe(AUTHOR, title="Too slow", category_id=soups, difficulty=easy, cook_time_minutes=90)
    repo.seed_recipe(AUTHOR, title="Too hard", category_id=soups, difficulty=hard, cook_time_minutes=20)
    repo.seed_recipe(AUTHOR, title="Wrong category", difficulty=easy, cook_time_minutes=20)
    response = client.get(BASE, params={"category_id": str(soups), "difficulty": "easy", "max_cook_time": 30})

    assert [i["title"] for i in response.json()["items"]] == ["Match"]


def test_list_sorts_and_paginates(client, repo):
    for title in ("Cherry", "Apple", "Banana"):
        repo.seed_recipe(AUTHOR, title=title)
    first = client.get(BASE, params={"sort": "title", "page": 1, "page_size": 2}).json()
    second = client.get(BASE, params={"sort": "title", "page": 2, "page_size": 2}).json()

    assert [i["title"] for i in first["items"]] == ["Apple", "Banana"] and first["has_next_page"] is True
    assert [i["title"] for i in second["items"]] == ["Cherry"] and second["has_previous_page"] is True
    assert client.get(BASE, params={"sort": "-title"}).json()["items"][0]["title"] == "Cherry"


def test_list_with_unknown_category_is_200_and_empty(client, repo):
    repo.seed_recipe(AUTHOR)
    response = client.get(BASE, params={"category_id": "00000000-0000-4000-8000-000000000000"})

    assert response.status_code == 200 and response.json()["items"] == [] and response.json()["total_count"] == 0


@pytest.mark.parametrize(
    "params",
    [
        {"page": 0},
        {"page": "x"},
        {"page_size": 0},
        {"page_size": 51},
        {"difficulty": "impossible"},
        {"difficulty": "1"},
        {"max_cook_time": -1},
        {"sort": "password"},
        {"sort": "--title"},
        {"category_id": "not-a-uuid"},
    ],
)
def test_list_with_invalid_params_is_422_problem_json(client, params):
    assert_problem(client.get(BASE, params=params), 422)


def test_list_page_size_boundaries_are_accepted(client):
    assert client.get(BASE, params={"page_size": 1}).status_code == 200
    assert client.get(BASE, params={"page_size": 50}).status_code == 200
