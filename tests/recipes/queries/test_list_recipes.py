import uuid
from datetime import UTC, datetime, timedelta

import pytest

from culinary_blog.recipes.enums import RecipeDifficulty, RecipeStatus
from culinary_blog.recipes.queries.list_recipes import ListRecipesHandler, ListRecipesQuery
from tests.recipes.fakes import ADMIN, AUTHOR, OTHER_AUTHOR, FakeRecipeRepository


def make_handler():
    repo = FakeRecipeRepository()
    return repo, ListRecipesHandler(repo)


def query(**overrides) -> ListRecipesQuery:
    return ListRecipesQuery(**({"page": 1, "page_size": 12, "sort": "-created_at"} | overrides))


def titles(out) -> list[str]:
    return [item.title for item in out.items]


@pytest.mark.anyio
async def test_guest_sees_only_published():
    repo, handler = make_handler()
    repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED, title="Published")
    repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT, title="Draft")
    repo.seed_recipe(AUTHOR, RecipeStatus.ARCHIVED, title="Archived")

    out = await handler.handle(query())

    assert titles(out) == ["Published"] and out.total_count == 1


@pytest.mark.anyio
async def test_author_sees_published_plus_own_unpublished_but_not_others():
    repo, handler = make_handler()
    repo.seed_recipe(OTHER_AUTHOR, RecipeStatus.PUBLISHED, title="Theirs published")
    repo.seed_recipe(OTHER_AUTHOR, RecipeStatus.DRAFT, title="Theirs draft")
    repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT, title="Mine draft")
    repo.seed_recipe(AUTHOR, RecipeStatus.ARCHIVED, title="Mine archived")

    out = await handler.handle(query(viewer=AUTHOR, sort="title"))

    assert titles(out) == ["Mine archived", "Mine draft", "Theirs published"]


@pytest.mark.anyio
async def test_admin_sees_every_status():
    repo, handler = make_handler()
    for status in RecipeStatus:
        repo.seed_recipe(AUTHOR, status, title=status.name)

    assert (await handler.handle(query(viewer=ADMIN))).total_count == 3


@pytest.mark.anyio
async def test_soft_deleted_recipes_are_excluded_even_for_admin():
    repo, handler = make_handler()
    repo.seed_recipe(AUTHOR, title="Gone").is_deleted = True
    repo.seed_recipe(AUTHOR, title="Here")

    assert titles(await handler.handle(query(viewer=ADMIN))) == ["Here"]


@pytest.mark.anyio
async def test_filters_combine():
    repo, handler = make_handler()
    soups, desserts = repo.add_category("Soups"), repo.add_category("Desserts")
    repo.seed_recipe(
        AUTHOR, title="Quick easy soup", category_id=soups, difficulty=RecipeDifficulty.EASY, cook_time_minutes=15
    )
    repo.seed_recipe(
        AUTHOR, title="Slow easy soup", category_id=soups, difficulty=RecipeDifficulty.EASY, cook_time_minutes=120
    )
    repo.seed_recipe(
        AUTHOR, title="Quick hard soup", category_id=soups, difficulty=RecipeDifficulty.HARD, cook_time_minutes=15
    )
    repo.seed_recipe(
        AUTHOR, title="Quick easy cake", category_id=desserts, difficulty=RecipeDifficulty.EASY, cook_time_minutes=15
    )

    assert (await handler.handle(query(category_id=soups))).total_count == 3
    assert (await handler.handle(query(difficulty=RecipeDifficulty.EASY))).total_count == 3
    both = await handler.handle(query(category_id=soups, difficulty=RecipeDifficulty.EASY, max_cook_time=30))
    assert titles(both) == ["Quick easy soup"]


@pytest.mark.anyio
async def test_max_cook_time_is_inclusive():
    repo, handler = make_handler()
    repo.seed_recipe(AUTHOR, title="Exactly 30", cook_time_minutes=30)
    repo.seed_recipe(AUTHOR, title="31 minutes", cook_time_minutes=31)

    assert titles(await handler.handle(query(max_cook_time=30))) == ["Exactly 30"]


@pytest.mark.anyio
async def test_unknown_category_yields_an_empty_page_not_an_error():
    repo, handler = make_handler()
    repo.seed_recipe(AUTHOR)

    out = await handler.handle(query(category_id=uuid.uuid4()))

    assert out.items == [] and out.total_count == 0 and out.total_pages == 0
    assert out.has_next_page is False and out.has_previous_page is False


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("sort", "expected"),
    [
        ("title", ["Apple", "Banana", "Cherry"]),
        ("-title", ["Cherry", "Banana", "Apple"]),
        ("cook_time_minutes", ["Banana", "Cherry", "Apple"]),
        ("-cook_time_minutes", ["Apple", "Cherry", "Banana"]),
        ("created_at", ["Cherry", "Apple", "Banana"]),
        ("-created_at", ["Banana", "Apple", "Cherry"]),
    ],
)
async def test_sorting(sort, expected):
    repo, handler = make_handler()
    now = datetime.now(UTC)
    for title, cook, age in (("Apple", 60, 2), ("Banana", 10, 1), ("Cherry", 30, 3)):
        repo.seed_recipe(AUTHOR, title=title, cook_time_minutes=cook, created_at=now - timedelta(days=age))

    assert titles(await handler.handle(query(sort=sort))) == expected


@pytest.mark.anyio
async def test_pagination_counts_and_flags():
    repo, handler = make_handler()
    for n in range(5):
        repo.seed_recipe(AUTHOR, title=f"Recipe {n}")

    first = await handler.handle(query(page=1, page_size=2, sort="title"))
    middle = await handler.handle(query(page=2, page_size=2, sort="title"))
    last = await handler.handle(query(page=3, page_size=2, sort="title"))
    beyond = await handler.handle(query(page=4, page_size=2, sort="title"))

    assert (first.total_count, first.total_pages, first.page, first.page_size) == (5, 3, 1, 2)
    assert titles(first) == ["Recipe 0", "Recipe 1"] and (first.has_previous_page, first.has_next_page) == (False, True)
    assert titles(middle) == ["Recipe 2", "Recipe 3"] and (middle.has_previous_page, middle.has_next_page) == (
        True,
        True,
    )
    assert titles(last) == ["Recipe 4"] and (last.has_previous_page, last.has_next_page) == (True, False)
    assert beyond.items == [] and beyond.total_count == 5 and beyond.has_next_page is False


@pytest.mark.anyio
async def test_summary_items_carry_the_public_summary_fields():
    repo, handler = make_handler()
    recipe = repo.seed_recipe(AUTHOR)
    (item,) = (await handler.handle(query())).items

    assert item.id == recipe.id and item.slug == recipe.slug and item.author_id == AUTHOR.user_id
    assert item.status == RecipeStatus.PUBLISHED and item.published_at is not None
