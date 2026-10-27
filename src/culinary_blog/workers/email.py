"""Email worker (FR-JOB-002, FR-AUTH-001): consumes `welcome_email` from the Job Queue Redis and sends it over SMTP.

Run: uv run culinary-blog-email-worker
One try plus three retries (1 min, 5 min, 30 min), then the job is parked in `welcome_email:dlq`.
"""

import asyncio
import html
import logging
from collections.abc import Awaitable, Callable
from email.message import EmailMessage

import aiosmtplib
from redis.asyncio import Redis

from culinary_blog.cache.redis import get_queue_redis
from culinary_blog.config import Settings, get_settings
from culinary_blog.jobs.queue import WELCOME_EMAIL
from culinary_blog.workers.base import JobWorker

logger = logging.getLogger(__name__)

WELCOME_HTML = """<!doctype html>
<html><body style="font-family: sans-serif">
<p>Hi {name},</p>
<p>Welcome to Culinary Blog. Your author account is ready, so you can start writing recipes.</p>
</body></html>"""


class WelcomeEmailWorker(JobWorker):
    max_attempts = 4  # 1 try + 3 retries
    backoff = (60, 300, 1800)

    def __init__(
        self,
        redis: Redis,
        settings: Settings,
        send: Callable[..., Awaitable[object]] = aiosmtplib.send,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self._settings = settings
        self._send = send
        super().__init__(redis, {WELCOME_EMAIL: self._send_welcome}, sleep)

    async def _send_welcome(self, payload: dict) -> None:
        message = EmailMessage()
        message["From"] = self._settings.smtp_from
        message["To"] = payload["email"]
        message["Subject"] = "Welcome to Culinary Blog"
        message.set_content(WELCOME_HTML.format(name=html.escape(payload["display_name"])), subtype="html")
        s = self._settings
        await self._send(
            message,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_username or None,
            password=s.smtp_password or None,
            start_tls=s.smtp_use_tls,
        )


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(WelcomeEmailWorker(get_queue_redis(), get_settings()).run())


if __name__ == "__main__":
    main()
