from fastapi.testclient import TestClient

from culinary_blog.recipes.enums import RecipeStatus
from tests.recipes.conftest import TOKENS
from tests.recipes.fakes import ADMIN, AUTHOR, OTHER_AUTHOR, FakeRecipeRepository


def as_user(client: TestClient, principal) -> None:
    client.cookies.set("access_token", TOKENS.create_access_token(principal.user_id, list(principal.roles)))


def seed_author_recipes(repo: FakeRecipeRepository, principal) -> None:
    category_id = repo.add_category()
    repo.seed_recipe(principal, RecipeStatus.DRAFT, category_id=category_id)
    repo.seed_recipe(principal, RecipeStatus.PUBLISHED, category_id=category_id)
    repo.seed_recipe(principal, RecipeStatus.ARCHIVED, category_id=category_id)


def test_guest_asking_for_an_author_filter_is_401(client, repo):
    seed_author_recipes(repo, AUTHOR)

    response = client.get("/api/v1/recipes", params={"author_id": "me"})

    assert response.status_code == 401


def test_owner_sees_all_own_statuses_with_counts(client, repo):
    as_user(client, AUTHOR)
    seed_author_recipes(repo, AUTHOR)
    seed_author_recipes(repo, OTHER_AUTHOR)  # someone else's recipes must not leak in

    body = client.get("/api/v1/recipes", params={"author_id": "me"}).json()

    assert body["total_count"] == 3
    assert {item["status"] for item in body["items"]} == {0, 1, 2}
    assert body["status_counts"] == {"draft": 1, "published": 1, "archived": 1}


def test_status_narrows_the_list_but_not_the_counts(client, repo):
    as_user(client, AUTHOR)
    seed_author_recipes(repo, AUTHOR)

    body = client.get("/api/v1/recipes", params={"author_id": "me", "status": "draft"}).json()

    assert [item["status"] for item in body["items"]] == [RecipeStatus.DRAFT.value]
    assert body["status_counts"]["published"] == 1


def test_author_cannot_list_another_authors_recipes(client, repo):
    as_user(client, AUTHOR)
    seed_author_recipes(repo, OTHER_AUTHOR)

    response = client.get("/api/v1/recipes", params={"author_id": str(OTHER_AUTHOR.user_id)})

    assert response.status_code == 403
    assert response.headers["content-type"].startswith("application/problem+json")


def test_admin_can_list_any_author_including_drafts(client, repo):
    as_user(client, ADMIN)
    seed_author_recipes(repo, OTHER_AUTHOR)

    body = client.get("/api/v1/recipes", params={"author_id": str(OTHER_AUTHOR.user_id)}).json()

    assert body["total_count"] == 3
    assert body["status_counts"] == {"draft": 1, "published": 1, "archived": 1}


def test_malformed_author_id_is_422(client):
    as_user(client, AUTHOR)

    assert client.get("/api/v1/recipes", params={"author_id": "not-an-id"}).status_code == 422


def test_guest_list_is_unchanged_and_has_no_counts(client, repo):
    seed_author_recipes(repo, AUTHOR)

    body = client.get("/api/v1/recipes").json()

    assert body["total_count"] == 1  # only the published one
    assert body["status_counts"] is None


def test_guest_status_filter_cannot_reveal_drafts(client, repo):
    seed_author_recipes(repo, AUTHOR)

    body = client.get("/api/v1/recipes", params={"status": "draft"}).json()

    assert body["items"] == [] and body["total_count"] == 0


def test_summary_carries_updated_at_and_row_version(client, repo):
    seed_author_recipes(repo, AUTHOR)

    item = client.get("/api/v1/recipes").json()["items"][0]

    assert "updated_at" in item and item["row_version"] == 0
