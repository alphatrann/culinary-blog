"""Sitemap XML (NFR-SEO-003). Pure: the worker and the on-the-fly path both emit these exact bytes."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from xml.etree import ElementTree

SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
STORED_KEY = "sitemap/sitemap.xml"  # where the sitemap worker keeps the generated file in object storage


@dataclass(frozen=True)
class SitemapUrl:
    path: str  # relative to the site origin, e.g. "/recipes/pho-bo"
    lastmod: datetime | None
    changefreq: str
    priority: str


def build_sitemap_xml(site_url: str, urls: Sequence[SitemapUrl]) -> bytes:
    root = ElementTree.Element("urlset", xmlns=SITEMAP_NS)
    for item in urls:
        node = ElementTree.SubElement(root, "url")
        ElementTree.SubElement(node, "loc").text = site_url.rstrip("/") + item.path
        if item.lastmod is not None:  # W3C date, UTC
            ElementTree.SubElement(node, "lastmod").text = item.lastmod.astimezone(UTC).date().isoformat()
        ElementTree.SubElement(node, "changefreq").text = item.changefreq
        ElementTree.SubElement(node, "priority").text = item.priority
    return ElementTree.tostring(root, encoding="utf-8", xml_declaration=True)
