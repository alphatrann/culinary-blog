import io
import json
import uuid

import pytest
from PIL import Image

from culinary_blog.jobs.queue import DELETE_FILE, RESIZE_IMAGE, dead_letter_queue
from culinary_blog.recipes.enums import RecipeStatus
from culinary_blog.recipes.models import RecipeImage
from culinary_blog.workers.image import MAX_ATTEMPTS, ImageWorker, render_variants
from tests.recipes.fakes import AUTHOR, FakeRecipeRepository, FakeStorage


class FakeRedis:
    def __init__(self) -> None:
        self.lists: dict[str, list[str]] = {}

    async def lpush(self, key: str, value: str) -> None:
        self.lists.setdefault(key, []).append(value)


def make_jpeg(size=(1600, 900)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, (200, 80, 40)).save(buffer, "JPEG")
    return buffer.getvalue()


def dims(data: bytes) -> tuple[int, int]:
    return Image.open(io.BytesIO(data)).size


async def no_sleep(_: float) -> None:
    return None


@pytest.fixture
def redis() -> FakeRedis:
    return FakeRedis()


@pytest.fixture
def storage() -> FakeStorage:
    return FakeStorage()


@pytest.fixture
def repo() -> FakeRecipeRepository:
    return FakeRecipeRepository()


@pytest.fixture
def worker(redis, storage, repo) -> ImageWorker:
    return ImageWorker(redis, storage, repo, sleep=no_sleep)  # type: ignore[arg-type]


async def seed_image(repo, storage, data: bytes) -> RecipeImage:
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT)
    url = await storage.upload(data, f"recipes/{recipe.id}", ".jpg", "image/jpeg")
    return await repo.add_image(RecipeImage(recipe_id=recipe.id, original_url=url))


def job(image: RecipeImage, **extra) -> str:
    return json.dumps({"image_id": str(image.id), "recipe_id": str(image.recipe_id), "attempts": 0} | extra)


def test_render_variants_sizes():
    medium, thumbnail = render_variants(make_jpeg((1600, 900)))
    assert dims(medium) == (800, 450)  # fitted inside 800x600, aspect ratio kept
    assert dims(thumbnail) == (300, 300)  # cropped to fill


def test_render_variants_never_upscales():
    medium, _ = render_variants(make_jpeg((400, 300)))
    assert dims(medium) == (400, 300)


@pytest.mark.anyio
async def test_resize_job_stores_variants_and_records_urls(worker, repo, storage):
    image = await seed_image(repo, storage, make_jpeg())
    await worker.process(RESIZE_IMAGE, job(image))

    assert image.medium_url in storage.objects and image.thumbnail_url in storage.objects
    assert dims(storage.objects[image.thumbnail_url]) == (300, 300)
    assert storage.objects[image.original_url]  # the original is untouched


@pytest.mark.anyio
async def test_resize_job_for_deleted_image_is_a_noop(worker, repo, storage, redis):
    image = await seed_image(repo, storage, make_jpeg())
    await repo.delete_image(image.recipe_id, image.id)
    await worker.process(RESIZE_IMAGE, job(image))
    assert len(storage.objects) == 1 and redis.lists == {}


@pytest.mark.anyio
async def test_failing_job_is_requeued_with_incremented_attempts(worker, repo, storage, redis):
    image = await seed_image(repo, storage, b"not an image")
    await worker.process(RESIZE_IMAGE, job(image))
    assert json.loads(redis.lists[RESIZE_IMAGE][0])["attempts"] == 1
    assert dead_letter_queue(RESIZE_IMAGE) not in redis.lists


@pytest.mark.anyio
async def test_job_goes_to_dlq_after_max_attempts(worker, repo, storage, redis):
    image = await seed_image(repo, storage, b"not an image")
    await worker.process(RESIZE_IMAGE, job(image, attempts=MAX_ATTEMPTS - 1))
    assert RESIZE_IMAGE not in redis.lists
    assert json.loads(redis.lists[dead_letter_queue(RESIZE_IMAGE)][0])["attempts"] == MAX_ATTEMPTS
    assert image.thumbnail_url is None  # graceful: the original stays usable


@pytest.mark.anyio
async def test_delete_file_job_removes_all_files_and_tolerates_missing_ones(worker, storage):
    url = await storage.upload(b"x", "recipes/a", ".jpg", "image/jpeg")
    missing = f"http://storage/recipes/a/{uuid.uuid4()}.jpg"
    await worker.process(DELETE_FILE, json.dumps({"urls": [url, missing], "attempts": 0}))
    assert storage.objects == {}
