from collections.abc import Awaitable, Callable

from pydantic import BaseModel

from culinary_blog.cache.service import Cache


class FakeCache(Cache):
    """In-memory `Cache`: records what was stored and invalidated, and can simulate an unavailable Redis."""

    def __init__(self, *, unavailable: bool = False) -> None:
        self.unavailable = unavailable
        self.store: dict[str, tuple[str, int]] = {}  # key -> (json, ttl)
        self.deleted: list[str] = []
        self.generation = 0
        self.loads = 0

    async def _through[T: BaseModel](
        self, key: str, ttl_seconds: int, model: type[T], loader: Callable[[], Awaitable[T]]
    ) -> T:
        if self.unavailable:
            self.loads += 1
            return await loader()
        if key in self.store:
            return model.model_validate_json(self.store[key][0])
        self.loads += 1
        value = await loader()
        self.store[key] = (value.model_dump_json(), ttl_seconds)
        return value

    async def get_or_load[T: BaseModel](
        self, key: str, ttl_seconds: int, model: type[T], loader: Callable[[], Awaitable[T]]
    ) -> T:
        return await self._through(key, ttl_seconds, model, loader)

    async def get_or_load_versioned[T: BaseModel](
        self,
        namespace: str,
        query_hash: str,
        ttl_seconds: int,
        model: type[T],
        loader: Callable[[], Awaitable[T]],
    ) -> T:
        return await self._through(f"{namespace}:v{self.generation}:{query_hash}", ttl_seconds, model, loader)

    async def get_or_load_swr[T: BaseModel](
        self, key: str, ttl_seconds: int, model: type[T], loader: Callable[[], Awaitable[T]]
    ) -> T:
        return await self._through(key, ttl_seconds, model, loader)

    async def delete(self, *keys: str) -> None:
        self.deleted.extend(keys)
        for key in keys:
            self.store.pop(key, None)

    async def bump_generation(self) -> None:
        self.generation += 1
