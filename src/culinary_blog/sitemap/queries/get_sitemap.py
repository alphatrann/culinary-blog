from dataclasses import dataclass

from culinary_blog.categories.repository import CategoryRepository
from culinary_blog.cqrs import Query, QueryHandler
from culinary_blog.errors import ServiceUnavailableError
from culinary_blog.recipes.repository import RecipeRepository
from culinary_blog.sitemap.builder import STORED_KEY, SitemapUrl, build_sitemap_xml
from culinary_blog.storage.service import FileStorageService

STATIC_URLS = (
    SitemapUrl("/", None, "daily", "1.0"),
    SitemapUrl("/categories", None, "weekly", "0.8"),
)


@dataclass(frozen=True)
class GetSitemapQuery(Query):
    pass


class GetSitemapHandler(QueryHandler[GetSitemapQuery, bytes]):
    """Serves the worker's stored XML from MinIO if present, else builds it from the database (no cache-aside)."""

    def __init__(
        self,
        recipes: RecipeRepository,
        categories: CategoryRepository,
        storage: FileStorageService,
        site_url: str,
    ) -> None:
        self._recipes = recipes
        self._categories = categories
        self._storage = storage
        self._site_url = site_url

    async def handle(self, query: GetSitemapQuery) -> bytes:
        try:
            stored = await self._storage.get_at(STORED_KEY)
        except ServiceUnavailableError:  # storage down: a fresh build beats a 503 for crawlers
            stored = None
        return stored if stored is not None else await self.build()

    async def build(self) -> bytes:
        recipes = await self._recipes.list_published_for_sitemap()
        categories = await self._categories.list_for_sitemap()
        urls = [
            *STATIC_URLS,
            *(SitemapUrl(f"/recipes/{slug}", lastmod, "weekly", "0.7") for slug, lastmod in recipes),
            *(SitemapUrl(f"/categories/{slug}", lastmod, "weekly", "0.6") for slug, lastmod in categories),
        ]
        return build_sitemap_xml(self._site_url, urls)
