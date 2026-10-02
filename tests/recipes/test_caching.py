"""M6b: cache-aside on the recipe read handlers and event-driven invalidation from the write handlers."""

import uuid

import pytest

from culinary_blog.cache import keys
from culinary_blog.errors import ForbiddenError, NotFoundError
from culinary_blog.recipes.commands.add_ingredient import AddIngredientCommand, AddIngredientHandler
from culinary_blog.recipes.commands.add_step import AddStepCommand, AddStepHandler
from culinary_blog.recipes.commands.create_recipe import CreateRecipeCommand, CreateRecipeHandler
from culinary_blog.recipes.commands.delete_recipe import DeleteRecipeCommand, DeleteRecipeHandler
from culinary_blog.recipes.commands.publish_recipe import PublishRecipeCommand, PublishRecipeHandler
from culinary_blog.recipes.commands.unpublish_recipe import UnpublishRecipeCommand, UnpublishRecipeHandler
from culinary_blog.recipes.commands.update_recipe import UpdateRecipeCommand, UpdateRecipeHandler
from culinary_blog.recipes.commands.upload_image import UploadImageCommand, UploadImageHandler
from culinary_blog.recipes.enums import RecipeStatus
from culinary_blog.recipes.models import RecipeIngredient, RecipeStep
from culinary_blog.recipes.queries.get_recipe import GetRecipeHandler, GetRecipeQuery
from culinary_blog.recipes.queries.list_recipes import ListRecipesHandler, ListRecipesQuery
from culinary_blog.recipes.queries.search_recipes import SearchRecipesHandler, SearchRecipesQuery
from culinary_blog.recipes.schemas import IngredientIn, StepIn
from culinary_blog.storage.images import JPEG
from tests.cache.fakes import FakeCache
from tests.recipes.fakes import (
    ADMIN,
    AUTHOR,
    OTHER_AUTHOR,
    FakeJobQueue,
    FakeRecipeRepository,
    FakeStorage,
    invalidator,
)


@pytest.fixture
def repo() -> FakeRecipeRepository:
    return FakeRecipeRepository()


@pytest.fixture
def cache() -> FakeCache:
    return FakeCache()


def list_query(**overrides) -> ListRecipesQuery:
    return ListRecipesQuery(**({"page": 1, "page_size": 12, "sort": "-created_at"} | overrides))


# --- reads ----------------------------------------------------------------------------------------------------------


@pytest.mark.anyio
async def test_guest_list_is_served_from_cache_after_the_first_read(repo, cache):
    handler = ListRecipesHandler(repo, cache)
    repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED, title="First")

    first = await handler.handle(list_query())
    repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED, title="Second")  # not visible until invalidated
    second = await handler.handle(list_query())

    assert first == second and second.total_count == 1
    assert cache.loads == 1


@pytest.mark.anyio
async def test_list_cache_key_includes_every_query_parameter(repo, cache):
    handler = ListRecipesHandler(repo, cache)
    repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED)

    await handler.handle(list_query())
    await handler.handle(list_query(page=2))
    await handler.handle(list_query(sort="title"))
    await handler.handle(list_query(max_cook_time=10))

    assert cache.loads == 4


@pytest.mark.anyio
async def test_list_uses_the_configured_ttl(repo, cache):
    await ListRecipesHandler(repo, cache, ttl_seconds=60).handle(list_query())

    assert [ttl for _, ttl in cache.store.values()] == [60]


@pytest.mark.anyio
async def test_signed_in_viewers_bypass_the_list_cache_so_drafts_never_enter_it(repo, cache):
    handler = ListRecipesHandler(repo, cache)
    repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT, title="Mine")

    mine = await handler.handle(list_query(viewer=AUTHOR))
    guest = await handler.handle(list_query())

    assert [i.title for i in mine.items] == ["Mine"]
    assert guest.items == []
    assert len(cache.store) == 1  # only the guest page was cached


@pytest.mark.anyio
async def test_search_is_cached_and_the_term_is_normalised(repo, cache):
    handler = SearchRecipesHandler(repo, cache)
    repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED, title="Pho Bo")

    await handler.handle(SearchRecipesQuery(q="Pho", page=1, page_size=12))
    again = await handler.handle(SearchRecipesQuery(q=" pho ", page=1, page_size=12))

    assert again.total_count == 1
    assert cache.loads == 1


@pytest.mark.anyio
async def test_detail_is_cached_but_a_cached_draft_is_still_forbidden_to_strangers(repo, cache):
    handler = GetRecipeHandler(repo, cache)
    draft = repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT)

    assert (await handler.handle(GetRecipeQuery(draft.slug, AUTHOR))).slug == draft.slug  # populates the cache
    assert (await handler.handle(GetRecipeQuery(draft.slug, ADMIN))).slug == draft.slug
    with pytest.raises(ForbiddenError):
        await handler.handle(GetRecipeQuery(draft.slug, OTHER_AUTHOR))
    with pytest.raises(ForbiddenError):
        await handler.handle(GetRecipeQuery(draft.slug))
    assert cache.loads == 1


@pytest.mark.anyio
async def test_detail_not_found_is_not_cached(repo, cache):
    with pytest.raises(NotFoundError):
        await GetRecipeHandler(repo, cache).handle(GetRecipeQuery("nope"))

    assert cache.store == {}


@pytest.mark.anyio
async def test_reads_still_work_when_the_cache_is_down(repo):
    cache = FakeCache(unavailable=True)
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED)

    assert (await ListRecipesHandler(repo, cache).handle(list_query())).total_count == 1
    assert (await GetRecipeHandler(repo, cache).handle(GetRecipeQuery(recipe.slug))).slug == recipe.slug


# --- invalidation ---------------------------------------------------------------------------------------------------


def draft_with_content(repo):
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT)
    repo.steps.append(RecipeStep(recipe_id=recipe.id, step_number=1, title="t", description="d"))
    repo.ingredients.append(RecipeIngredient(recipe_id=recipe.id, name="x", order_index=0))
    return recipe


@pytest.mark.anyio
async def test_create_bumps_lists_only(repo, cache):
    category_id = repo.add_category()
    command = CreateRecipeCommand(AUTHOR, "Bun Cha", "d", category_id, 1, 1, 1)

    await CreateRecipeHandler(repo, invalidator(cache)).handle(command)

    assert cache.generation == 1 and cache.deleted == []


@pytest.mark.anyio
async def test_publish_drops_detail_and_category_counts_and_bumps_lists(repo, cache):
    recipe = draft_with_content(repo)

    await PublishRecipeHandler(repo, invalidator(cache)).handle(PublishRecipeCommand(AUTHOR, recipe.id))

    assert cache.deleted == [keys.recipe(recipe.slug), keys.CATEGORIES_ALL]
    assert cache.generation == 1


@pytest.mark.anyio
async def test_publishing_an_already_published_recipe_invalidates_nothing(repo, cache):
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED)
    repo.steps.append(RecipeStep(recipe_id=recipe.id, step_number=1, title="t", description="d"))
    repo.ingredients.append(RecipeIngredient(recipe_id=recipe.id, name="x", order_index=0))

    await PublishRecipeHandler(repo, invalidator(cache)).handle(PublishRecipeCommand(AUTHOR, recipe.id))

    assert cache.deleted == [] and cache.generation == 0


@pytest.mark.anyio
async def test_unpublish_and_delete_drop_detail_and_category_counts_and_bump_lists(repo, cache):
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED)

    await UnpublishRecipeHandler(repo, invalidator(cache)).handle(UnpublishRecipeCommand(AUTHOR, recipe.id))
    await DeleteRecipeHandler(repo, invalidator(cache)).handle(DeleteRecipeCommand(AUTHOR, recipe.id))

    assert cache.deleted == [keys.recipe(recipe.slug), keys.CATEGORIES_ALL] * 2
    assert cache.generation == 2


@pytest.mark.anyio
async def test_a_published_recipe_disappears_from_a_warm_list_after_unpublish(repo, cache):
    lists = ListRecipesHandler(repo, cache)
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED)
    assert (await lists.handle(list_query())).total_count == 1

    await UnpublishRecipeHandler(repo, invalidator(cache)).handle(UnpublishRecipeCommand(AUTHOR, recipe.id))

    assert (await lists.handle(list_query())).total_count == 0


@pytest.mark.anyio
async def test_update_drops_the_detail_and_bumps_lists_but_keeps_category_counts_unless_the_category_changed(
    repo, cache
):
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED)
    other_category = repo.add_category("Other")

    def update(category_id):
        return UpdateRecipeCommand(AUTHOR, recipe.id, recipe.row_version, "T", "d", category_id, 1, 1, 1)

    await UpdateRecipeHandler(repo, invalidator(cache)).handle(update(recipe.category_id))
    assert cache.deleted == [keys.recipe(recipe.slug)]

    await UpdateRecipeHandler(repo, invalidator(cache)).handle(update(other_category))
    assert cache.deleted[1:] == [keys.recipe(recipe.slug), keys.CATEGORIES_ALL]
    assert cache.generation == 2


@pytest.mark.anyio
async def test_children_changes_drop_only_the_detail(repo, cache):
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED)

    await AddStepHandler(repo, invalidator(cache)).handle(
        AddStepCommand(AUTHOR, recipe.id, StepIn(title="a", description="b"))
    )
    await AddIngredientHandler(repo, invalidator(cache)).handle(
        AddIngredientCommand(AUTHOR, recipe.id, IngredientIn(name="x"))
    )
    await UploadImageHandler(repo, FakeStorage(), FakeJobQueue(), invalidator(cache)).handle(
        UploadImageCommand(AUTHOR, recipe.id, b"x", JPEG, None)
    )

    assert cache.deleted == [keys.recipe(recipe.slug)] * 3
    assert cache.generation == 0


@pytest.mark.anyio
async def test_failed_commands_do_not_invalidate(repo, cache):
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED)

    with pytest.raises(ForbiddenError):
        await DeleteRecipeHandler(repo, invalidator(cache)).handle(DeleteRecipeCommand(OTHER_AUTHOR, recipe.id))
    with pytest.raises(NotFoundError):
        await DeleteRecipeHandler(repo, invalidator(cache)).handle(DeleteRecipeCommand(AUTHOR, uuid.uuid4()))

    assert cache.deleted == [] and cache.generation == 0
