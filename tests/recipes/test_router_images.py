"""Integration tests (HTTP → handlers → fakes) for recipe images (M4, FR-RCP-008)."""

import uuid

import pytest

from culinary_blog.jobs.queue import DELETE_FILE, RESIZE_IMAGE
from culinary_blog.recipes.enums import RecipeStatus
from culinary_blog.storage.images import MAX_IMAGE_BYTES
from tests.recipes.fakes import ADMIN, AUTHOR, OTHER_AUTHOR, READER
from tests.recipes.test_router import BASE, as_user, assert_problem

JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 64
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
WEBP = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 64
AVIF = b"\x00\x00\x00\x1cftypavif" + b"\x00" * 64


@pytest.fixture
def draft(repo):
    return repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT)


def images_url(recipe, image_id=None, suffix="") -> str:
    return f"{BASE}/{recipe.id}/images" + (f"/{image_id}" if image_id else "") + suffix


def upload(client, recipe, data=JPEG, content_type="image/jpeg", **form):
    return client.post(images_url(recipe), files={"file": ("photo.bin", data, content_type)}, data=form)


# --- upload ---------------------------------------------------------------------------------------------------------


def test_upload_first_image_is_primary_and_enqueues_resize(client, draft, storage, queue):
    as_user(client, AUTHOR)
    response = upload(client, draft, alt_text="Tô phở")
    assert response.status_code == 201
    body = response.json()
    assert body["is_primary"] is True and body["alt_text"] == "Tô phở"
    assert body["original_url"].startswith(f"http://storage/recipes/{draft.id}/") and body["original_url"].endswith(
        ".jpg"
    )
    assert body["medium_url"] is None and body["thumbnail_url"] is None
    assert storage.objects[body["original_url"]] == JPEG
    assert queue.jobs == [(RESIZE_IMAGE, {"image_id": body["id"], "recipe_id": str(draft.id)})]


def test_second_upload_is_not_primary(client, draft):
    as_user(client, AUTHOR)
    upload(client, draft)
    second = upload(client, draft, PNG, "image/png")
    assert second.status_code == 201 and second.json()["is_primary"] is False
    assert second.json()["original_url"].endswith(".png")


@pytest.mark.parametrize(("data", "content_type"), [(PNG, "image/png"), (WEBP, "image/webp"), (AVIF, "image/avif")])
def test_upload_accepts_all_allowed_formats(client, draft, data, content_type):
    as_user(client, AUTHOR)
    assert upload(client, draft, data, content_type).status_code == 201


def test_admin_can_upload_to_someone_elses_recipe(client, draft):
    as_user(client, ADMIN)
    assert upload(client, draft).status_code == 201


def test_upload_succeeds_even_if_the_queue_is_down(client, draft, queue):
    queue.fail = True
    as_user(client, AUTHOR)
    assert upload(client, draft).status_code == 201


@pytest.mark.parametrize(
    ("data", "content_type"),
    [
        (JPEG, "text/plain"),  # A1: MIME not allowed
        (JPEG, "image/gif"),
        (PNG, "image/jpeg"),  # A3: magic bytes disagree with the declared type
        (b"<?php echo 1;", "image/jpeg"),  # A3: not an image at all
        (b"", "image/jpeg"),
        pytest.param(JPEG + b"\x00" * MAX_IMAGE_BYTES, "image/jpeg", id="over-5mb"),  # A2
    ],
)
def test_upload_rejects_invalid_files_400(client, draft, storage, data, content_type):
    as_user(client, AUTHOR)
    assert_problem(upload(client, draft, data, content_type), 400)
    assert storage.objects == {}


def test_upload_rejects_too_long_alt_text_422(client, draft):
    as_user(client, AUTHOR)
    assert_problem(upload(client, draft, alt_text="x" * 201), 422)


def test_upload_missing_file_422(client, draft):
    as_user(client, AUTHOR)
    assert_problem(client.post(images_url(draft), data={"alt_text": "x"}), 422)


def test_upload_storage_down_503(client, draft, storage, repo):
    storage.fail = True
    as_user(client, AUTHOR)
    assert_problem(upload(client, draft), 503)
    assert repo.images == []


def test_upload_requires_authentication_401(client, draft):
    assert_problem(upload(client, draft), 401)


@pytest.mark.parametrize("principal", [OTHER_AUTHOR, READER])
def test_upload_by_non_owner_403(client, draft, principal):
    as_user(client, principal)
    assert_problem(upload(client, draft), 403)


def test_upload_unknown_recipe_404(client):
    as_user(client, AUTHOR)
    response = client.post(f"{BASE}/{uuid.uuid4()}/images", files={"file": ("a.jpg", JPEG, "image/jpeg")})
    assert_problem(response, 404)


# --- set primary ----------------------------------------------------------------------------------------------------


def test_set_primary_moves_the_flag(client, draft, repo):
    as_user(client, AUTHOR)
    first = upload(client, draft).json()
    second = upload(client, draft).json()
    response = client.patch(images_url(draft, second["id"], "/primary"))
    assert response.status_code == 200 and response.json()["is_primary"] is True
    primary = {i.id: i.is_primary for i in repo.images}
    assert primary[uuid.UUID(first["id"])] is False and primary[uuid.UUID(second["id"])] is True

    # idempotent
    assert client.patch(images_url(draft, second["id"], "/primary")).status_code == 200
    assert sum(i.is_primary for i in repo.images) == 1


def test_set_primary_unknown_image_404(client, draft):
    as_user(client, AUTHOR)
    assert_problem(client.patch(images_url(draft, uuid.uuid4(), "/primary")), 404)


def test_set_primary_image_of_another_recipe_404(client, draft, repo):
    other = repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT, title="Other")
    as_user(client, AUTHOR)
    foreign = upload(client, other).json()
    assert_problem(client.patch(images_url(draft, foreign["id"], "/primary")), 404)


def test_set_primary_by_non_owner_403(client, draft):
    as_user(client, AUTHOR)
    image = upload(client, draft).json()
    as_user(client, OTHER_AUTHOR)
    assert_problem(client.patch(images_url(draft, image["id"], "/primary")), 403)


# --- delete ---------------------------------------------------------------------------------------------------------


def test_delete_primary_promotes_the_first_remaining_image(client, draft, repo, queue):
    as_user(client, AUTHOR)
    first = upload(client, draft).json()
    second = upload(client, draft).json()
    third = upload(client, draft).json()
    queue.jobs.clear()

    response = client.delete(images_url(draft, first["id"]))
    assert response.status_code == 204 and response.content == b""
    live = {str(i.id): i.is_primary for i in repo.images if not i.is_deleted}
    assert live == {second["id"]: True, third["id"]: False}
    assert queue.jobs == [(DELETE_FILE, {"urls": [first["original_url"]]})]


def test_delete_non_primary_keeps_primary(client, draft, repo):
    as_user(client, AUTHOR)
    first = upload(client, draft).json()
    second = upload(client, draft).json()
    assert client.delete(images_url(draft, second["id"])).status_code == 204
    assert [(str(i.id), i.is_primary) for i in repo.images if not i.is_deleted] == [(first["id"], True)]


def test_delete_last_image_leaves_none(client, draft, repo):
    as_user(client, AUTHOR)
    image = upload(client, draft).json()
    assert client.delete(images_url(draft, image["id"])).status_code == 204
    assert not [i for i in repo.images if not i.is_deleted]


def test_delete_twice_404(client, draft):
    as_user(client, AUTHOR)
    image = upload(client, draft).json()
    client.delete(images_url(draft, image["id"]))
    assert_problem(client.delete(images_url(draft, image["id"])), 404)


def test_delete_by_non_owner_403(client, draft):
    as_user(client, AUTHOR)
    image = upload(client, draft).json()
    as_user(client, OTHER_AUTHOR)
    assert_problem(client.delete(images_url(draft, image["id"])), 403)


def test_delete_requires_authentication_401(client, draft):
    assert_problem(client.delete(images_url(draft, uuid.uuid4())), 401)


def test_uploaded_images_show_up_on_recipe_detail(client, draft):
    as_user(client, AUTHOR)
    upload(client, draft)
    detail = client.get(f"{BASE}/{draft.slug}")
    assert detail.status_code == 200
    assert [i["is_primary"] for i in detail.json()["images"]] == [True]
