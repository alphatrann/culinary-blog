"""Cache key names and ADR-0003 default TTLs. Kept in one place so readers and invalidators can't drift apart."""

import hashlib
import json

CATEGORY_TTL_SECONDS = 3600
RECIPE_TTL_SECONDS = 1800
SEARCH_TTL_SECONDS = 300

CATEGORIES_ALL = "categories:all"

# Query-shaped keys are `{namespace}:v{generation}:{query_hash}`; a generation bump drops a whole namespace.
NS_RECIPE_LIST = "recipes:list"
NS_SEARCH = "search"


def recipe(slug: str) -> str:
    return f"recipe:{slug}"


def category_detail_namespace(slug: str) -> str:
    return f"category:{slug}"


def query_hash(**params: object) -> str:
    """Stable digest of a query's parameters (order-independent; enums/UUIDs via `str`)."""
    canonical = json.dumps(params, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()[:32]
