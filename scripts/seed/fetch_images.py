"""Download one real photo per recipe from Wikimedia Commons into scripts/seed/images/ + manifest.json.

Run: uv run python scripts/seed/fetch_images.py [--force]
Attribution (author, licence, source page) is stored in the manifest for every image.
"""

import asyncio
import json
import re
import sys
import unicodedata
from pathlib import Path

import httpx
from dishes import CATALOGUE

HERE = Path(__file__).parent
IMAGES = HERE / "images"
MANIFEST = HERE / "manifest.json"
API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "culinary-blog-seed/0.1 (alphatran.forwork@gmail.com)"}
BAD_TITLE = re.compile(
    r"menu|map|logo|shop|street|market|stall|vendor|restaurant|sign|poster|diagram|chef|people", re.I
)


def normalize(text: str) -> str:
    text = text.replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def title_matches(title: str, query: str) -> bool:
    """Every query word must appear in the file name, so full-text hits on unrelated descriptions are rejected."""
    words = normalize(title)
    return all(token in words for token in normalize(query).split())


def slug(index: int) -> str:
    return f"recipe-{index:03d}"


async def search(client: httpx.AsyncClient, query: str) -> list[dict]:
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f"{query} filetype:bitmap",
        "gsrnamespace": 6,
        "gsrlimit": 20,
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": 1200,
    }
    for attempt in range(5):
        response = await client.get(API, params=params)
        if response.status_code == 429:
            await asyncio.sleep(2 * (attempt + 1))
            continue
        response.raise_for_status()
        pages = response.json().get("query", {}).get("pages", {})
        return sorted(pages.values(), key=lambda p: p.get("index", 0))
    return []


def usable(page: dict, query: str) -> bool:
    info = (page.get("imageinfo") or [{}])[0]
    return (
        info.get("mime") == "image/jpeg"
        and info.get("width", 0) >= 900
        and info.get("height", 0) >= 600
        and info.get("width", 0) / max(info.get("height", 1), 1) < 2.2
        and not BAD_TITLE.search(page["title"])
        and title_matches(page["title"], query)
    )


def strip_html(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value or "").strip()


USED: set[str] = set()


async def fetch_one(client: httpx.AsyncClient, index: int, title: str, queries: list[str]) -> dict | None:
    target = IMAGES / f"{slug(index)}.jpg"
    for query in queries:
        for page in await search(client, query):
            if not usable(page, query) or page["title"] in USED:
                continue
            info = page["imageinfo"][0]
            meta = info.get("extmetadata", {})
            download = await client.get(info["thumburl"])
            if download.status_code != 200 or len(download.content) > 4_500_000:
                continue
            target.write_bytes(download.content)
            USED.add(page["title"])
            return {
                "index": index,
                "title": title,
                "query": query,
                "file": target.name,
                "commons_title": page["title"],
                "source_url": info["descriptionurl"],
                "author": strip_html(meta.get("Artist", {}).get("value", "")),
                "license": meta.get("LicenseShortName", {}).get("value", ""),
            }
    return None


async def main() -> None:
    force = "--force" in sys.argv
    IMAGES.mkdir(exist_ok=True)
    manifest: dict[str, dict] = json.loads(MANIFEST.read_text("utf-8")) if MANIFEST.exists() else {}
    dishes = [(title, queries) for _, recipes in CATALOGUE for title, queries in recipes]
    semaphore = asyncio.Semaphore(3)

    async with httpx.AsyncClient(headers=HEADERS, timeout=60, follow_redirects=True) as client:

        async def job(index: int, title: str, queries: list[str]) -> None:
            key = slug(index)
            if not force and key in manifest and (IMAGES / manifest[key]["file"]).exists():
                return
            async with semaphore:
                result = await fetch_one(client, index, title, queries)
            status = f"<- {result['commons_title']}" if result else ""
            print(f"{'ok  ' if result else 'MISS'} {index:3d} {title} {status}")
            if result:
                manifest[key] = result

        await asyncio.gather(*(job(i, t, q) for i, (t, q) in enumerate(dishes, start=1)))

    MANIFEST.write_text(json.dumps(dict(sorted(manifest.items())), ensure_ascii=False, indent=2), "utf-8")
    print(f"{len(manifest)}/{len(dishes)} images")


if __name__ == "__main__":
    asyncio.run(main())
