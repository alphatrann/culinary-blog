import uuid

from fastapi.testclient import TestClient

from culinary_blog.recipes.enums import RecipeStatus
from tests.recipes.conftest import TOKENS
from tests.recipes.fakes import ADMIN, AUTHOR, OTHER_AUTHOR, FakeRecipeRepository


def as_user(client: TestClient, principal) -> None:
    client.cookies.set("access_token", TOKENS.create_access_token(principal.user_id, list(principal.roles)))


def test_owner_gets_draft_by_id_with_etag(client, repo: FakeRecipeRepository):
    as_user(client, AUTHOR)
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT, category_id=repo.add_category())

    response = client.get(f"/api/v1/recipes/{recipe.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(recipe.id) and response.json()["status"] == RecipeStatus.DRAFT.value
    assert response.headers["ETag"] == f'"{recipe.row_version}"'


def test_admin_gets_any_recipe_by_id(client, repo: FakeRecipeRepository):
    as_user(client, ADMIN)
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT, category_id=repo.add_category())

    assert client.get(f"/api/v1/recipes/{recipe.id}").status_code == 200


def test_other_author_is_403_problem_json(client, repo: FakeRecipeRepository):
    as_user(client, OTHER_AUTHOR)
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT, category_id=repo.add_category())

    response = client.get(f"/api/v1/recipes/{recipe.id}")

    assert response.status_code == 403
    assert response.headers["content-type"].startswith("application/problem+json")


def test_guest_is_401(client, repo: FakeRecipeRepository):
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED, category_id=repo.add_category())

    assert client.get(f"/api/v1/recipes/{recipe.id}").status_code == 401


def test_unknown_id_is_404(client):
    as_user(client, AUTHOR)

    response = client.get(f"/api/v1/recipes/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")


def test_slug_route_still_serves_published_recipes(client, repo: FakeRecipeRepository):
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED, category_id=repo.add_category())

    response = client.get(f"/api/v1/recipes/{recipe.slug}")

    assert response.status_code == 200 and response.json()["slug"] == recipe.slug
