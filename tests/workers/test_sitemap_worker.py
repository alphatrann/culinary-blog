import json
import time
from datetime import UTC, datetime

import pytest

from culinary_blog.config import Settings
from culinary_blog.jobs.queue import SITEMAP, dead_letter_queue
from culinary_blog.sitemap.builder import STORED_KEY
from culinary_blog.sitemap.queries.get_sitemap import GetSitemapHandler
from culinary_blog.workers.sitemap import SitemapWorker
from tests.recipes.fakes import FakeStorage
from tests.sitemap.fakes import SITE, FakeCategoryRepository, FakeRecipeRepository


class FakeRedis:
    def __init__(self) -> None:
        self.lists: dict[str, list[str]] = {}

    async def lpush(self, key: str, value: str) -> None:
        self.lists.setdefault(key, []).append(value)


class Pings:
    """Records Google pings. `fail` simulates Google answering 404 or being unreachable."""

    def __init__(self) -> None:
        self.urls: list[str] = []
        self.fail = False

    async def __call__(self, sitemap_url: str) -> None:
        self.urls.append(sitemap_url)
        if self.fail:
            raise ConnectionError("google down")


class Sleeps:
    async def __call__(self, seconds: float) -> None:
        return None


def job(**extra) -> str:
    return json.dumps({"attempts": 0} | extra)


@pytest.fixture
def redis() -> FakeRedis:
    return FakeRedis()


@pytest.fixture
def storage() -> FakeStorage:
    return FakeStorage()


@pytest.fixture
def recipes() -> FakeRecipeRepository:
    repository = FakeRecipeRepository()
    repository.published = [("pho-bo", datetime(2026, 10, 1, tzinfo=UTC))]
    return repository


@pytest.fixture
def pings() -> Pings:
    return Pings()


@pytest.fixture
def worker(redis, storage, recipes, pings) -> SitemapWorker:
    handler = GetSitemapHandler(recipes, FakeCategoryRepository(), storage, SITE)
    return SitemapWorker(redis, storage, handler, Settings(site_url=SITE), ping=pings, sleep=Sleeps())


@pytest.mark.anyio
async def test_success_stores_xml_and_pings_google(worker, storage, redis, pings):
    await worker.process(SITEMAP, job())

    stored = storage.objects[f"http://storage/{STORED_KEY}"]
    assert f"{SITE}/recipes/pho-bo".encode() in stored
    assert pings.urls == [f"{SITE}/sitemap.xml"]
    assert redis.lists == {}


@pytest.mark.anyio
async def test_failed_google_ping_does_not_fail_the_job(worker, storage, redis, pings):
    pings.fail = True

    await worker.process(SITEMAP, job())

    assert f"http://storage/{STORED_KEY}" in storage.objects  # stored before the ping
    assert redis.lists == {}  # no retry, no dead letter


@pytest.mark.anyio
async def test_build_failure_is_retried_with_backoff(worker, recipes, redis):
    recipes.fail = True
    before = time.time()

    await worker.process(SITEMAP, job())

    (retry,) = redis.lists[SITEMAP]
    retry = json.loads(retry)
    assert retry["attempts"] == 1
    assert before + 60 <= retry["run_at"] <= time.time() + 60


@pytest.mark.anyio
async def test_job_is_dead_lettered_after_the_last_attempt(worker, recipes, redis):
    recipes.fail = True

    await worker.process(SITEMAP, job(attempts=2))  # the third and last attempt

    assert SITEMAP not in redis.lists
    assert json.loads(redis.lists[dead_letter_queue(SITEMAP)][0])["attempts"] == 3


@pytest.mark.anyio
async def test_future_run_at_is_requeued_without_running(worker, storage, redis):
    await worker.process(SITEMAP, job(run_at=time.time() + 600))

    assert storage.objects == {}
    assert json.loads(redis.lists[SITEMAP][0])["attempts"] == 0
