import pytest

from culinary_blog.recipes.enums import RecipeDifficulty, RecipeStatus
from culinary_blog.recipes.queries.search_recipes import SearchRecipesHandler, SearchRecipesQuery
from tests.recipes.fakes import AUTHOR, FakeRecipeRepository


def make_handler():
    repo = FakeRecipeRepository()
    return repo, SearchRecipesHandler(repo)


def query(**overrides) -> SearchRecipesQuery:
    return SearchRecipesQuery(**({"q": "pho", "page": 1, "page_size": 12} | overrides))


def titles(out) -> list[str]:
    return [item.title for item in out.items]


@pytest.mark.anyio
async def test_only_published_recipes_match():
    repo, handler = make_handler()
    repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED, title="Pho Bo")
    repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT, title="Pho Ga")
    repo.seed_recipe(AUTHOR, RecipeStatus.ARCHIVED, title="Pho Chay")

    out = await handler.handle(query())

    assert titles(out) == ["Pho Bo"] and out.total_count == 1


@pytest.mark.anyio
async def test_search_is_diacritic_insensitive():
    repo, handler = make_handler()
    repo.seed_recipe(AUTHOR, title="Phở Bò Hà Nội")

    out = await handler.handle(query(q="pho"))

    assert titles(out) == ["Phở Bò Hà Nội"]


@pytest.mark.anyio
async def test_search_is_case_insensitive():
    repo, handler = make_handler()
    repo.seed_recipe(AUTHOR, title="Grilled Salmon")

    out = await handler.handle(query(q="SALMON"))

    assert titles(out) == ["Grilled Salmon"]


@pytest.mark.anyio
async def test_no_match_returns_empty_page_not_an_error():
    repo, handler = make_handler()
    repo.seed_recipe(AUTHOR, title="Pho Bo")

    out = await handler.handle(query(q="xyzzy"))

    assert out.items == [] and out.total_count == 0 and out.total_pages == 0


@pytest.mark.anyio
async def test_closer_match_ranks_first():
    repo, handler = make_handler()
    repo.seed_recipe(AUTHOR, title="Pho")
    repo.seed_recipe(AUTHOR, title="Pho Bo Vien Ha Noi Dac Biet")

    out = await handler.handle(query(q="pho"))

    assert titles(out)[0] == "Pho"
    assert out.items[0].relevance_score >= out.items[1].relevance_score


@pytest.mark.anyio
async def test_filters_combine():
    repo, handler = make_handler()
    soups, desserts = repo.add_category("Soups"), repo.add_category("Desserts")
    repo.seed_recipe(
        AUTHOR, title="Pho Bo Soup", category_id=soups, difficulty=RecipeDifficulty.EASY, cook_time_minutes=15
    )
    repo.seed_recipe(
        AUTHOR, title="Pho Ga Soup", category_id=soups, difficulty=RecipeDifficulty.HARD, cook_time_minutes=15
    )
    repo.seed_recipe(AUTHOR, title="Pho Cake", category_id=desserts, cook_time_minutes=15)

    both = await handler.handle(query(q="pho bo", category_id=soups, difficulty=RecipeDifficulty.EASY))

    assert titles(both) == ["Pho Bo Soup"]


@pytest.mark.anyio
async def test_max_cook_time_is_inclusive():
    repo, handler = make_handler()
    repo.seed_recipe(AUTHOR, title="Pho Quick", cook_time_minutes=30)
    repo.seed_recipe(AUTHOR, title="Pho Slow", cook_time_minutes=31)

    out = await handler.handle(query(q="pho", max_cook_time=30))

    assert titles(out) == ["Pho Quick"]


@pytest.mark.anyio
async def test_pagination_counts_and_flags():
    repo, handler = make_handler()
    for n in range(5):
        repo.seed_recipe(AUTHOR, title=f"Pho {n}")

    first = await handler.handle(query(q="pho", page=1, page_size=2))
    last = await handler.handle(query(q="pho", page=3, page_size=2))

    assert (first.total_count, first.total_pages) == (5, 3)
    assert first.has_previous_page is False and first.has_next_page is True
    assert len(last.items) == 1 and last.has_next_page is False and last.has_previous_page is True


@pytest.mark.anyio
async def test_results_carry_the_public_summary_fields_and_relevance_score():
    repo, handler = make_handler()
    recipe = repo.seed_recipe(AUTHOR, title="Pho Bo")

    (item,) = (await handler.handle(query())).items

    assert item.id == recipe.id and item.slug == recipe.slug and item.author_id == AUTHOR.user_id
    assert item.relevance_score > 0
