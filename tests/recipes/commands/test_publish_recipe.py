import uuid
from datetime import UTC, datetime

import pytest

from culinary_blog.errors import ForbiddenError, NotFoundError, UnprocessableError
from culinary_blog.recipes.commands.publish_recipe import PublishRecipeCommand, PublishRecipeHandler
from culinary_blog.recipes.commands.unpublish_recipe import UnpublishRecipeCommand, UnpublishRecipeHandler
from culinary_blog.recipes.enums import RecipeStatus
from culinary_blog.recipes.models import RecipeIngredient, RecipeStep
from tests.recipes.fakes import ADMIN, AUTHOR, OTHER_AUTHOR, READER, FakeRecipeRepository


def draft(repo, *, steps=1, ingredients=1, **overrides):
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT, **overrides)
    repo.steps += [
        RecipeStep(recipe_id=recipe.id, step_number=n, title="t", description="d") for n in range(1, steps + 1)
    ]
    repo.ingredients += [RecipeIngredient(recipe_id=recipe.id, name="x", order_index=n) for n in range(ingredients)]
    return recipe


@pytest.mark.anyio
async def test_publish_sets_status_and_first_published_at():
    repo = FakeRecipeRepository()
    recipe = draft(repo)
    out = await PublishRecipeHandler(repo).handle(PublishRecipeCommand(AUTHOR, recipe.id))

    assert out.status == RecipeStatus.PUBLISHED and out.published_at is not None and out.row_version == 1


@pytest.mark.anyio
@pytest.mark.parametrize("steps,ingredients", [(0, 0), (1, 0), (0, 1)])
async def test_publish_blocked_without_a_step_and_an_ingredient(steps, ingredients):
    repo = FakeRecipeRepository()
    recipe = draft(repo, steps=steps, ingredients=ingredients)
    with pytest.raises(UnprocessableError):
        await PublishRecipeHandler(repo).handle(PublishRecipeCommand(AUTHOR, recipe.id))
    assert recipe.status == RecipeStatus.DRAFT and recipe.published_at is None


@pytest.mark.anyio
async def test_soft_deleted_children_do_not_count():
    repo = FakeRecipeRepository()
    recipe = draft(repo)
    repo.steps[0].is_deleted = True
    with pytest.raises(UnprocessableError):
        await PublishRecipeHandler(repo).handle(PublishRecipeCommand(AUTHOR, recipe.id))


@pytest.mark.anyio
async def test_publish_is_idempotent_and_does_not_touch_the_recipe():
    repo = FakeRecipeRepository()
    recipe = draft(repo)
    handler = PublishRecipeHandler(repo)
    first = await handler.handle(PublishRecipeCommand(AUTHOR, recipe.id))
    second = await handler.handle(PublishRecipeCommand(AUTHOR, recipe.id))

    assert second.row_version == first.row_version and second.published_at == first.published_at


@pytest.mark.anyio
async def test_already_published_recipe_skips_the_children_check():
    repo = FakeRecipeRepository()
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED)  # no steps/ingredients, but already published
    out = await PublishRecipeHandler(repo).handle(PublishRecipeCommand(AUTHOR, recipe.id))
    assert out.status == RecipeStatus.PUBLISHED and out.row_version == 0


@pytest.mark.anyio
async def test_republish_keeps_the_original_published_at():
    repo = FakeRecipeRepository()
    original = datetime(2026, 1, 1, tzinfo=UTC)
    recipe = draft(repo, published_at=original)
    out = await PublishRecipeHandler(repo).handle(PublishRecipeCommand(AUTHOR, recipe.id))
    assert out.published_at == original


@pytest.mark.anyio
async def test_unpublish_returns_to_draft_and_is_idempotent():
    repo = FakeRecipeRepository()
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED)
    handler = UnpublishRecipeHandler(repo)
    first = await handler.handle(UnpublishRecipeCommand(AUTHOR, recipe.id))
    second = await handler.handle(UnpublishRecipeCommand(AUTHOR, recipe.id))

    assert first.status == RecipeStatus.DRAFT and first.published_at is not None
    assert second.status == RecipeStatus.DRAFT and second.row_version == first.row_version


@pytest.mark.anyio
async def test_admin_can_publish_and_unpublish_any_recipe():
    repo = FakeRecipeRepository()
    recipe = draft(repo)
    assert (await PublishRecipeHandler(repo).handle(PublishRecipeCommand(ADMIN, recipe.id))).status == 1
    assert (await UnpublishRecipeHandler(repo).handle(UnpublishRecipeCommand(ADMIN, recipe.id))).status == 0


@pytest.mark.anyio
@pytest.mark.parametrize("actor", [OTHER_AUTHOR, READER])
async def test_forbidden_for_non_owner(actor):
    repo = FakeRecipeRepository()
    recipe = draft(repo)
    with pytest.raises(ForbiddenError):
        await PublishRecipeHandler(repo).handle(PublishRecipeCommand(actor, recipe.id))
    with pytest.raises(ForbiddenError):
        await UnpublishRecipeHandler(repo).handle(UnpublishRecipeCommand(actor, recipe.id))


@pytest.mark.anyio
async def test_unknown_recipe_is_not_found():
    repo = FakeRecipeRepository()
    with pytest.raises(NotFoundError):
        await PublishRecipeHandler(repo).handle(PublishRecipeCommand(AUTHOR, uuid.uuid4()))
    with pytest.raises(NotFoundError):
        await UnpublishRecipeHandler(repo).handle(UnpublishRecipeCommand(AUTHOR, uuid.uuid4()))
