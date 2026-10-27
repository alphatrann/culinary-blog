from datetime import UTC, datetime, timedelta, timezone
from xml.etree import ElementTree

from culinary_blog.sitemap.builder import SITEMAP_NS, SitemapUrl, build_sitemap_xml

SITE = "https://culinary.example/"


def parse(xml: bytes) -> ElementTree.Element:
    return ElementTree.fromstring(xml)


def test_entries_have_absolute_loc_and_all_child_fields():
    xml = build_sitemap_xml(SITE, [SitemapUrl("/recipes/pho", datetime(2026, 10, 1, 9, tzinfo=UTC), "weekly", "0.7")])

    url = parse(xml).find(f"{{{SITEMAP_NS}}}url")
    assert url is not None
    assert url.findtext(f"{{{SITEMAP_NS}}}loc") == "https://culinary.example/recipes/pho"  # trailing slash not doubled
    assert url.findtext(f"{{{SITEMAP_NS}}}lastmod") == "2026-10-01"
    assert url.findtext(f"{{{SITEMAP_NS}}}changefreq") == "weekly"
    assert url.findtext(f"{{{SITEMAP_NS}}}priority") == "0.7"


def test_lastmod_is_utc_date_and_omitted_when_unknown():
    local = datetime(2026, 10, 1, 1, 30, tzinfo=timezone(timedelta(hours=7)))  # 2026-09-30 18:30 UTC
    xml = build_sitemap_xml(SITE, [SitemapUrl("/", None, "daily", "1.0"), SitemapUrl("/x", local, "weekly", "0.5")])

    urls = parse(xml).findall(f"{{{SITEMAP_NS}}}url")
    assert urls[0].find(f"{{{SITEMAP_NS}}}lastmod") is None
    assert urls[1].findtext(f"{{{SITEMAP_NS}}}lastmod") == "2026-09-30"


def test_text_is_escaped_and_declaration_present():
    xml = build_sitemap_xml(SITE, [SitemapUrl("/recipes/a&b<c>", None, "weekly", "0.7")])

    assert xml.startswith(b"<?xml")
    assert b"a&amp;b&lt;c&gt;" in xml
    assert parse(xml).find(f"{{{SITEMAP_NS}}}url/{{{SITEMAP_NS}}}loc").text == "https://culinary.example/recipes/a&b<c>"
