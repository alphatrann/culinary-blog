"""Image worker (FR-JOB-002, FR-FILE-002): consumes `resize_image` and `delete_file` from the Job Queue Redis.

Run: uv run culinary-blog-image-worker
Failed jobs are retried up to MAX_ATTEMPTS times, then parked in `<queue>:dlq`.
"""

import asyncio
import io
import uuid
from collections.abc import Awaitable, Callable

from PIL import Image, ImageOps
from redis.asyncio import Redis

from culinary_blog.cache.redis import get_cache_redis, get_queue_redis
from culinary_blog.cache.service import RedisCache
from culinary_blog.config import get_settings
from culinary_blog.database.session import async_session_factory
from culinary_blog.jobs.queue import DELETE_FILE, RESIZE_IMAGE
from culinary_blog.logging import configure_logging
from culinary_blog.recipes.cache import RecipeCacheInvalidator
from culinary_blog.recipes.repository import RecipeRepository
from culinary_blog.storage.minio_storage import MinioFileStorage
from culinary_blog.storage.service import FileStorageService
from culinary_blog.workers.base import JobWorker

MAX_ATTEMPTS = 3
THUMBNAIL_SIZE = (300, 300)  # cropped to fill
MEDIUM_SIZE = (800, 600)  # fitted inside, aspect ratio kept, never upscaled


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


class ImageWorker(JobWorker):
    max_attempts = MAX_ATTEMPTS
    backoff = (2, 4)  # seconds before attempts 2 and 3

    def __init__(
        self,
        redis: Redis,
        storage: FileStorageService,
        repository: RecipeRepository,
        cache: RecipeCacheInvalidator,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self._storage = storage
        self._repository = repository
        self._cache = cache
        super().__init__(redis, {RESIZE_IMAGE: self._resize_image, DELETE_FILE: self._delete_files}, sleep)

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
            return
        # The cached recipe detail still lists the image without its variants.
        recipe = await self._repository.get_by_id(image.recipe_id)
        if recipe is not None:
            await self._cache.detail_changed(recipe.slug)

    async def _delete_files(self, payload: dict) -> None:
        for url in payload["urls"]:
            await self._storage.delete(url)


def main() -> None:
    configure_logging()
    worker = ImageWorker(
        get_queue_redis(),
        MinioFileStorage(get_settings()),
        RecipeRepository(async_session_factory),
        RecipeCacheInvalidator(RedisCache(get_cache_redis())),
    )
    asyncio.run(worker.run())


if __name__ == "__main__":
    main()
