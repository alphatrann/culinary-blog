from fastapi import APIRouter, Response

from culinary_blog.sitemap.queries.get_sitemap import GetSitemapHandler, GetSitemapQuery


class SitemapRouter:
    """HTTP adapter for the sitemap query: returns the XML bytes as-is."""

    def __init__(self, get_sitemap: GetSitemapHandler) -> None:
        self._get_sitemap = get_sitemap
        self.router = APIRouter(tags=["seo"])
        self.router.add_api_route("/sitemap.xml", self.sitemap, methods=["GET"], response_class=Response)

    async def sitemap(self) -> Response:
        return Response(content=await self._get_sitemap.handle(GetSitemapQuery()), media_type="text/xml")
