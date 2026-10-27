from fastapi import APIRouter

from culinary_blog.categories.repository import CategoryRepository
from culinary_blog.config import get_settings
from culinary_blog.database.session import async_session_factory, read_session_factory
from culinary_blog.recipes.repository import RecipeRepository
from culinary_blog.sitemap.queries.get_sitemap import GetSitemapHandler
from culinary_blog.sitemap.router import SitemapRouter
from culinary_blog.storage.minio_storage import MinioFileStorage
from culinary_blog.storage.service import FileStorageService


def build_get_sitemap(storage: FileStorageService) -> GetSitemapHandler:
    """Shared by the API router and the sitemap worker, so both bind the same repositories and site URL."""
    return GetSitemapHandler(
        RecipeRepository(async_session_factory, read_session_factory),
        CategoryRepository(async_session_factory, read_session_factory),
        storage,
        get_settings().site_url,
    )


def build_sitemap_router() -> APIRouter:
    """Composition root for the sitemap module: the only place that binds concrete dependencies."""
    return SitemapRouter(build_get_sitemap(MinioFileStorage(get_settings()))).router
