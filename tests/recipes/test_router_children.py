"""Integration tests (HTTP → handlers → fake repository) for ingredients, steps and publish (M3b, M3c)."""

import uuid

import pytest

from culinary_blog.recipes.enums import RecipeStatus
from tests.recipes.fakes import ADMIN, AUTHOR, OTHER_AUTHOR, READER
from tests.recipes.test_router import BASE, as_user, assert_problem


@pytest.fixture
def draft(repo):
    return repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT)


def ingredients_url(recipe, ingredient_id=None) -> str:
    return f"{BASE}/{recipe.id}/ingredients" + (f"/{ingredient_id}" if ingredient_id else "")


def steps_url(recipe, step_id=None) -> str:
    return f"{BASE}/{recipe.id}/steps" + (f"/{step_id}" if step_id else "")


STEP = {"title": "Ninh xương", "description": "Ninh 3 tiếng"}
INGREDIENT = {"name": "Thịt bò", "quantity": 500, "unit": "g"}


# --- ingredients ----------------------------------------------------------------------------------------------------


def test_add_update_delete_ingredient_happy_path(client, draft):
    as_user(client, AUTHOR)
    created = client.post(ingredients_url(draft), json=INGREDIENT)
    assert created.status_code == 201
    body = created.json()
    assert body["name"] == "Thịt bò" and body["quantity"] == 500 and body["order_index"] == 0

    updated = client.put(ingredients_url(draft, body["id"]), json={"name": "Muối"})
    assert updated.status_code == 200
    assert updated.json()["quantity"] is None and updated.json()["unit"] is None

    deleted = client.delete(ingredients_url(draft, body["id"]))
    assert deleted.status_code == 204 and deleted.content == b""
    assert_problem(client.put(ingredients_url(draft, body["id"]), json={"name": "x"}), 404)


@pytest.mark.parametrize(
    "body",
    [
        {"name": "Muối", "quantity": 1},
        {"name": "Muối", "unit": "g"},
        {"name": "Muối", "quantity": 0, "unit": "g"},
        {"name": "Muối", "quantity": -2, "unit": "g"},
        {"name": ""},
        {"name": "x" * 101},
    ],
)
def test_add_ingredient_invalid_body_is_422(client, draft, body):
    as_user(client, AUTHOR)
    assert_problem(client.post(ingredients_url(draft), json=body), 422)


def test_ingredient_endpoints_require_authentication(client, draft):
    assert_problem(client.post(ingredients_url(draft), json=INGREDIENT), 401)
    assert_problem(client.delete(ingredients_url(draft, uuid.uuid4())), 401)


@pytest.mark.parametrize("actor", [OTHER_AUTHOR, READER])
def test_ingredient_writes_forbidden_for_non_owner(client, draft, actor):
    as_user(client, AUTHOR)
    created = client.post(ingredients_url(draft), json=INGREDIENT).json()
    as_user(client, actor)

    assert_problem(client.post(ingredients_url(draft), json=INGREDIENT), 403)
    assert_problem(client.put(ingredients_url(draft, created["id"]), json={"name": "x"}), 403)
    assert_problem(client.delete(ingredients_url(draft, created["id"])), 403)


def test_admin_can_manage_ingredients_of_any_recipe(client, draft):
    as_user(client, ADMIN)
    assert client.post(ingredients_url(draft), json=INGREDIENT).status_code == 201


def test_ingredient_on_unknown_recipe_or_id_is_404(client, draft):
    as_user(client, AUTHOR)
    ghost = uuid.uuid4()
    assert_problem(client.post(f"{BASE}/{ghost}/ingredients", json=INGREDIENT), 404)
    assert_problem(client.delete(ingredients_url(draft, ghost)), 404)


def test_malformed_uuid_path_is_422(client):
    as_user(client, AUTHOR)
    assert_problem(client.post(f"{BASE}/not-a-uuid/ingredients", json=INGREDIENT), 422)


# --- steps ----------------------------------------------------------------------------------------------------------


def test_steps_autonumber_and_delete_renumbers(client, draft):
    as_user(client, AUTHOR)
    first = client.post(steps_url(draft), json=STEP)
    second = client.post(steps_url(draft), json=STEP | {"title": "Nêm nếm"})
    assert first.status_code == second.status_code == 201
    assert (first.json()["step_number"], second.json()["step_number"]) == (1, 2)

    assert client.delete(steps_url(draft, first.json()["id"])).status_code == 204

    detail = client.get(f"{BASE}/{draft.slug}").json()
    assert [(s["title"], s["step_number"]) for s in detail["steps"]] == [("Nêm nếm", 1)]


def test_client_supplied_step_number_is_ignored(client, draft):
    as_user(client, AUTHOR)
    response = client.post(steps_url(draft), json=STEP | {"step_number": 99})
    assert response.status_code == 201 and response.json()["step_number"] == 1


def test_update_step_keeps_its_number(client, draft):
    as_user(client, AUTHOR)
    client.post(steps_url(draft), json=STEP)
    second = client.post(steps_url(draft), json=STEP).json()
    response = client.put(
        steps_url(draft, second["id"]), json={"title": "Mới", "description": "Mô tả", "duration_minutes": 7}
    )

    assert response.status_code == 200
    assert (response.json()["title"], response.json()["duration_minutes"], response.json()["step_number"]) == (
        "Mới",
        7,
        2,
    )


@pytest.mark.parametrize(
    "body",
    [
        {"description": "d"},
        {"title": "t"},
        {"title": "", "description": "d"},
        {"title": "t", "description": "   "},
        {"title": "t" * 201, "description": "d"},
        {"title": "t", "description": "d" * 2001},
        {"title": "t", "description": "d", "duration_minutes": -1},
    ],
)
def test_add_step_invalid_body_is_422(client, draft, body):
    as_user(client, AUTHOR)
    assert_problem(client.post(steps_url(draft), json=body), 422)


def test_step_endpoints_require_authentication(client, draft):
    assert_problem(client.post(steps_url(draft), json=STEP), 401)


@pytest.mark.parametrize("actor", [OTHER_AUTHOR, READER])
def test_step_writes_forbidden_for_non_owner(client, draft, actor):
    as_user(client, AUTHOR)
    step = client.post(steps_url(draft), json=STEP).json()
    as_user(client, actor)

    assert_problem(client.post(steps_url(draft), json=STEP), 403)
    assert_problem(client.put(steps_url(draft, step["id"]), json=STEP), 403)
    assert_problem(client.delete(steps_url(draft, step["id"])), 403)


def test_step_on_unknown_recipe_or_id_is_404(client, draft):
    as_user(client, AUTHOR)
    assert_problem(client.post(f"{BASE}/{uuid.uuid4()}/steps", json=STEP), 404)
    assert_problem(client.delete(steps_url(draft, uuid.uuid4())), 404)


# --- publish / unpublish --------------------------------------------------------------------------------------------


def test_publish_without_steps_and_ingredients_is_422(client, draft):
    as_user(client, AUTHOR)
    response = client.patch(f"{BASE}/{draft.id}/publish")

    assert_problem(response, 422)
    assert client.get(f"{BASE}/{draft.slug}").json()["status"] == 0


def test_publish_with_only_one_kind_of_child_is_422(client, draft):
    as_user(client, AUTHOR)
    client.post(steps_url(draft), json=STEP)
    assert_problem(client.patch(f"{BASE}/{draft.id}/publish"), 422)


def test_publish_then_guest_sees_it_then_unpublish_hides_it(client, draft):
    as_user(client, AUTHOR)
    client.post(steps_url(draft), json=STEP)
    client.post(ingredients_url(draft), json=INGREDIENT)

    published = client.patch(f"{BASE}/{draft.id}/publish")
    assert published.status_code == 200
    assert published.json()["status"] == 1 and published.json()["published_at"] is not None
    assert published.headers["etag"] == '"1"'

    client.cookies.clear()
    assert client.get(f"{BASE}/{draft.slug}").status_code == 200
    assert [r["slug"] for r in client.get(BASE).json()["items"]] == [draft.slug]

    as_user(client, AUTHOR)
    unpublished = client.patch(f"{BASE}/{draft.id}/unpublish")
    assert unpublished.status_code == 200 and unpublished.json()["status"] == 0

    client.cookies.clear()
    assert_problem(client.get(f"{BASE}/{draft.slug}"), 403)
    assert client.get(BASE).json()["items"] == []


def test_publish_and_unpublish_are_idempotent(client, draft):
    as_user(client, AUTHOR)
    client.post(steps_url(draft), json=STEP)
    client.post(ingredients_url(draft), json=INGREDIENT)

    first = client.patch(f"{BASE}/{draft.id}/publish").json()
    again = client.patch(f"{BASE}/{draft.id}/publish")
    assert again.status_code == 200 and again.json()["published_at"] == first["published_at"]

    client.patch(f"{BASE}/{draft.id}/unpublish")
    assert client.patch(f"{BASE}/{draft.id}/unpublish").status_code == 200


def test_publish_requires_authentication_and_ownership(client, draft):
    assert_problem(client.patch(f"{BASE}/{draft.id}/publish"), 401)
    as_user(client, OTHER_AUTHOR)
    assert_problem(client.patch(f"{BASE}/{draft.id}/publish"), 403)
    assert_problem(client.patch(f"{BASE}/{draft.id}/unpublish"), 403)


def test_publish_unknown_recipe_is_404(client):
    as_user(client, AUTHOR)
    assert_problem(client.patch(f"{BASE}/{uuid.uuid4()}/publish"), 404)
    assert_problem(client.patch(f"{BASE}/{uuid.uuid4()}/unpublish"), 404)
