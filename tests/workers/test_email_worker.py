import json
import time
import uuid

import pytest

from culinary_blog.config import Settings
from culinary_blog.jobs.queue import WELCOME_EMAIL, dead_letter_queue
from culinary_blog.workers.email import WelcomeEmailWorker


class FakeRedis:
    def __init__(self) -> None:
        self.lists: dict[str, list[str]] = {}

    async def lpush(self, key: str, value: str) -> None:
        self.lists.setdefault(key, []).append(value)


class FakeSmtp:
    """Records what would have been sent. `fail` simulates an SMTP outage."""

    def __init__(self) -> None:
        self.sent: list[tuple[object, dict]] = []
        self.fail = False

    async def __call__(self, message, **kwargs) -> None:
        if self.fail:
            raise ConnectionError("smtp down")
        self.sent.append((message, kwargs))


class Sleeps:
    def __init__(self) -> None:
        self.calls: list[float] = []

    async def __call__(self, seconds: float) -> None:
        self.calls.append(seconds)


def job(**extra) -> str:
    payload = {"user_id": str(uuid.uuid4()), "email": "cook@example.com", "display_name": "<Cook>", "attempts": 0}
    return json.dumps(payload | extra)


@pytest.fixture
def redis() -> FakeRedis:
    return FakeRedis()


@pytest.fixture
def smtp() -> FakeSmtp:
    return FakeSmtp()


@pytest.fixture
def sleeps() -> Sleeps:
    return Sleeps()


@pytest.fixture
def worker(redis, smtp, sleeps) -> WelcomeEmailWorker:
    return WelcomeEmailWorker(redis, Settings(), send=smtp, sleep=sleeps)


@pytest.mark.anyio
async def test_sends_welcome_email_with_escaped_name(worker, smtp, redis):
    await worker.process(WELCOME_EMAIL, job())

    ((message, kwargs),) = smtp.sent
    assert message["To"] == "cook@example.com"
    assert message["Subject"] == "Welcome to Culinary Blog"
    html_body = message.get_body(("html",)).get_content()
    assert "Hi &lt;Cook&gt;," in html_body  # display name is escaped, not injected as markup
    assert kwargs["hostname"] == "localhost" and kwargs["port"] == 1025 and kwargs["start_tls"] is False
    assert redis.lists == {}


@pytest.mark.anyio
async def test_future_run_at_is_requeued_without_using_an_attempt(worker, smtp, redis, sleeps):
    await worker.process(WELCOME_EMAIL, job(run_at=time.time() + 1800))

    assert smtp.sent == []
    (requeued,) = redis.lists[WELCOME_EMAIL]
    assert json.loads(requeued)["attempts"] == 0
    assert sleeps.calls == [1]  # idle briefly so a not-yet-due job does not spin the loop
    assert dead_letter_queue(WELCOME_EMAIL) not in redis.lists


@pytest.mark.anyio
async def test_failure_is_retried_with_backoff_delay(worker, smtp, redis):
    smtp.fail = True
    before = time.time()
    await worker.process(WELCOME_EMAIL, job())

    (retry,) = redis.lists[WELCOME_EMAIL]
    retry = json.loads(retry)
    assert retry["attempts"] == 1
    assert before + 60 <= retry["run_at"] <= time.time() + 60  # first backoff step


@pytest.mark.anyio
async def test_job_goes_to_dlq_after_the_last_attempt(worker, smtp, redis):
    smtp.fail = True
    await worker.process(WELCOME_EMAIL, job(attempts=3))  # the 4th and last attempt

    assert WELCOME_EMAIL not in redis.lists
    assert json.loads(redis.lists[dead_letter_queue(WELCOME_EMAIL)][0])["attempts"] == 4
