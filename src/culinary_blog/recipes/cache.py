from culinary_blog.cache import keys
from culinary_blog.cache.service import Cache


class RecipeCacheInvalidator:
    """Event-driven invalidation for recipe writes (NFR-PERF-003). Called by command handlers after the DB commit.

    Failures are swallowed by the cache itself: a missed delete is bounded by the TTL, never a failed write.
    """

    def __init__(self, cache: Cache) -> None:
        self._cache = cache

    async def created(self) -> None:
        """A new draft is visible to nobody but its author, so only list generations need to move."""
        await self._cache.bump_generation()

    async def updated(self, slug: str, *, category_changed: bool) -> None:
        await self._cache.delete(keys.recipe(slug), *([keys.CATEGORIES_ALL] if category_changed else []))
        await self._cache.bump_generation()

    async def visibility_changed(self, slug: str) -> None:
        """Publish / unpublish / delete: the recipe, every list and search page, and category recipe counts change."""
        await self._cache.delete(keys.recipe(slug), keys.CATEGORIES_ALL)
        await self._cache.bump_generation()

    async def detail_changed(self, slug: str) -> None:
        """Steps, ingredients and images only appear in the detail view."""
        await self._cache.delete(keys.recipe(slug))
