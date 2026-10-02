from culinary_blog.cache import keys
from culinary_blog.cache.service import Cache


class CategoryCacheInvalidator:
    """Event-driven invalidation for category writes (FR-CAT-003/004)."""

    def __init__(self, cache: Cache) -> None:
        self._cache = cache

    async def created(self) -> None:
        await self._cache.delete(keys.CATEGORIES_ALL)

    async def updated(self) -> None:
        """Also moves the generation: category pages embed the category's name and description."""
        await self._cache.delete(keys.CATEGORIES_ALL)
        await self._cache.bump_generation()
