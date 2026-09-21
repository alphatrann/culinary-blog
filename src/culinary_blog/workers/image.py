"""Image worker (FR-JOB-002, FR-FILE-002): consumes `resize_image` and `delete_file` from the Job Queue Redis.

Run: uv run culinary-blog-image-worker
Failed jobs are retried up to MAX_ATTEMPTS times, then parked in `<queue>:dlq`.
"""

import asyncio
import io
import json
import logging
import uuid
from collections.abc import Awaitable, Callable

from PIL import Image, ImageOps
from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from culinary_blog.cache.redis import get_queue_redis
from culinary_blog.config import get_settings
from culinary_blog.database.session import async_session_factory
from culinary_blog.jobs.queue import DELETE_FILE, RESIZE_IMAGE, dead_letter_queue
from culinary_blog.recipes.repository import RecipeRepository
from culinary_blog.storage.minio_storage import MinioFileStorage
from culinary_blog.storage.service import FileStorageService

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3
THUMBNAIL_SIZE = (300, 300)  # cropped to fill
MEDIUM_SIZE = (800, 600)  # fitted inside, aspect ratio kept, never upscaled
# Must stay below the Redis client's socket timeout (redis-py default: 5 s), or every idle BRPOP would raise.
POLL_TIMEOUT_SECONDS = 2
RECONNECT_DELAY_SECONDS = 1


def render_variants(original: bytes) -> tuple[bytes, bytes]:
    """CPU-bound: return (medium, thumbnail) JPEG bytes for an original image."""
    with Image.open(io.BytesIO(original)) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")
    medium = image.copy()
    medium.thumbnail(MEDIUM_SIZE, Image.Resampling.LANCZOS)
    thumbnail = ImageOps.fit(image, THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
    return _jpeg(medium), _jpeg(thumbnail)


def _jpeg(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, "JPEG", quality=85, optimize=True)
    return buffer.getvalue()


class ImageWorker:
    def __init__(
        self,
        redis: Redis,
        storage: FileStorageService,
        repository: RecipeRepository,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self._redis = redis
        self._storage = storage
        self._repository = repository
        self._sleep = sleep
        self._handlers = {RESIZE_IMAGE: self._resize_image, DELETE_FILE: self._delete_files}

    async def run(self) -> None:
        logger.info("image worker started")
        while True:
            try:
                popped = await self._redis.brpop(list(self._handlers), timeout=POLL_TIMEOUT_SECONDS)  # type: ignore[misc]
            except (RedisConnectionError, RedisTimeoutError):  # Redis restarting or briefly unreachable: keep polling
                logger.warning("job queue unavailable, retrying", exc_info=True)
                await self._sleep(RECONNECT_DELAY_SECONDS)
                continue
            if popped is None:
                continue
            queue, raw = popped
            await self.process(queue.decode() if isinstance(queue, bytes) else queue, raw)

    async def process(self, queue: str, raw: bytes | str) -> None:
        """Run one job; on failure re-enqueue it, or dead-letter it once attempts are exhausted."""
        payload = json.loads(raw)
        try:
            await self._handlers[queue](payload)
        except Exception:
            attempts = payload.get("attempts", 0) + 1
            logger.exception("job failed", extra={"queue": queue, "attempts": attempts})
            if attempts < MAX_ATTEMPTS:
                await self._sleep(2**attempts)
                await self._redis.lpush(queue, json.dumps({**payload, "attempts": attempts}))  # type: ignore[misc]
            else:
                await self._redis.lpush(dead_letter_queue(queue), json.dumps({**payload, "attempts": attempts}))  # type: ignore[misc]

    async def _resize_image(self, payload: dict) -> None:
        image = await self._repository.get_image(uuid.UUID(payload["recipe_id"]), uuid.UUID(payload["image_id"]))
        if image is None:  # deleted before the worker got to it: nothing to do
            return
        medium, thumbnail = await asyncio.to_thread(render_variants, await self._storage.download(image.original_url))
        folder = f"recipes/{image.recipe_id}"
        medium_url = await self._storage.upload(medium, folder, ".jpg", "image/jpeg")
        thumbnail_url = await self._storage.upload(thumbnail, folder, ".jpg", "image/jpeg")
        if not await self._repository.set_image_variants(image.id, medium_url=medium_url, thumbnail_url=thumbnail_url):
            await self._storage.delete(medium_url)  # the image was deleted meanwhile; don't leak the variants
            await self._storage.delete(thumbnail_url)

    async def _delete_files(self, payload: dict) -> None:
        for url in payload["urls"]:
            await self._storage.delete(url)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    worker = ImageWorker(get_queue_redis(), MinioFileStorage(get_settings()), RecipeRepository(async_session_factory))
    asyncio.run(worker.run())


if __name__ == "__main__":
    main()
