import uuid
from decimal import Decimal

import pytest

from culinary_blog.errors import ConflictError, ForbiddenError, NotFoundError, UnprocessableError
from culinary_blog.recipes.commands.update_recipe import UpdateRecipeCommand, UpdateRecipeHandler
from culinary_blog.recipes.enums import RecipeDifficulty, RecipeStatus
from culinary_blog.recipes.models import Recipe, RecipeIngredient, RecipeStep
from culinary_blog.recipes.schemas import NutritionIn
from tests.recipes.fakes import ADMIN, AUTHOR, NO_ROLES, OTHER_AUTHOR, READER, FakeRecipeRepository


def make_handler():
    repo = FakeRecipeRepository()
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED, title="Pho Bo", nutrition_calories=Decimal("100"))
    return repo, UpdateRecipeHandler(repo), recipe


def command(recipe: Recipe, repo: FakeRecipeRepository, actor=AUTHOR, **overrides) -> UpdateRecipeCommand:
    fields = {
        "recipe_id": recipe.id,
        "expected_version": recipe.row_version,
        "title": "Phở Bò Tái",
        "description": "Updated description",
        "category_id": recipe.category_id,
        "prep_time_minutes": 45,
        "cook_time_minutes": 90,
        "servings": 6,
        "difficulty": RecipeDifficulty.HARD,
    } | overrides
    return UpdateRecipeCommand(actor, **fields)


@pytest.mark.anyio
async def test_owner_updates_fields_and_row_version_is_bumped():
    repo, handler, recipe = make_handler()
    out = await handler.handle(command(recipe, repo))

    assert (out.title, out.description, out.prep_time_minutes, out.cook_time_minutes, out.servings) == (
        "Phở Bò Tái",
        "Updated description",
        45,
        90,
        6,
    )
    assert out.difficulty == RecipeDifficulty.HARD and out.row_version == 1
    assert repo.recipes[recipe.id].row_version == 1 and repo.recipes[recipe.id].updated_at is not None


@pytest.mark.anyio
async def test_update_keeps_slug_status_author_and_publication_untouched():
    repo, handler, recipe = make_handler()
    slug, published_at = recipe.slug, recipe.published_at
    out = await handler.handle(command(recipe, repo))

    assert out.slug == slug and out.status == RecipeStatus.PUBLISHED
    assert out.author_id == AUTHOR.user_id and out.published_at == published_at


@pytest.mark.anyio
async def test_update_can_move_recipe_to_another_category():
    repo, handler, recipe = make_handler()
    other = repo.add_category("Desserts")

    assert (await handler.handle(command(recipe, repo, category_id=other))).category_id == other


@pytest.mark.anyio
async def test_update_returns_existing_steps_and_ingredients_unchanged():
    repo, handler, recipe = make_handler()
    repo.steps.append(RecipeStep(recipe_id=recipe.id, step_number=1, title="Boil", description="x"))
    repo.ingredients.append(RecipeIngredient(recipe_id=recipe.id, name="Salt", order_index=0))
    out = await handler.handle(command(recipe, repo))

    assert [s.title for s in out.steps] == ["Boil"] and [i.name for i in out.ingredients] == ["Salt"]


@pytest.mark.anyio
async def test_admin_can_update_someone_elses_recipe():
    repo, handler, recipe = make_handler()

    assert (await handler.handle(command(recipe, repo, ADMIN))).row_version == 1
    assert repo.recipes[recipe.id].author_id == AUTHOR.user_id


@pytest.mark.anyio
async def test_nutrition_is_replaced_when_supplied():
    repo, handler, recipe = make_handler()
    out = await handler.handle(command(recipe, repo, nutrition=NutritionIn(protein=Decimal("25"))))

    assert out.nutrition.protein == 25 and out.nutrition.calories is None  # replaced wholesale, not merged


@pytest.mark.anyio
async def test_nutrition_is_left_alone_when_omitted():
    repo, handler, recipe = make_handler()
    out = await handler.handle(command(recipe, repo, nutrition=None))

    assert out.nutrition.calories == 100


# --- optimistic concurrency -----------------------------------------------------------------------------------------


@pytest.mark.anyio
async def test_stale_row_version_conflicts_and_changes_nothing():
    repo, handler, recipe = make_handler()
    await handler.handle(command(recipe, repo, title="First edit wins"))  # someone else got there first

    with pytest.raises(ConflictError, match="thay đổi"):
        await handler.handle(command(recipe, repo, expected_version=0, title="Stale edit loses"))
    assert repo.recipes[recipe.id].title == "First edit wins" and repo.recipes[recipe.id].row_version == 1


@pytest.mark.anyio
async def test_future_row_version_also_conflicts():
    repo, handler, recipe = make_handler()

    with pytest.raises(ConflictError):
        await handler.handle(command(recipe, repo, expected_version=5))


@pytest.mark.anyio
async def test_two_sequential_updates_with_fresh_versions_both_succeed():
    repo, handler, recipe = make_handler()
    first = await handler.handle(command(recipe, repo))
    second = await handler.handle(command(recipe, repo, expected_version=first.row_version, title="Second edit"))

    assert (first.row_version, second.row_version) == (1, 2)


@pytest.mark.anyio
async def test_losing_the_compare_and_swap_race_is_a_conflict():
    """The row passes the read check, then another writer bumps it before our UPDATE lands."""

    class RacyRepository(FakeRecipeRepository):
        async def update(self, recipe_id, expected_version, values):
            self.recipes[recipe_id].row_version += 1  # the concurrent writer
            return await super().update(recipe_id, expected_version, values)

    repo = RacyRepository()
    recipe = repo.seed_recipe(AUTHOR)

    with pytest.raises(ConflictError):
        await UpdateRecipeHandler(repo).handle(command(recipe, repo))


# --- authorization / lookup / validation ----------------------------------------------------------------------------


@pytest.mark.anyio
@pytest.mark.parametrize("actor", [OTHER_AUTHOR, READER, NO_ROLES])
async def test_non_owner_is_forbidden_and_nothing_is_written(actor):
    repo, handler, recipe = make_handler()

    with pytest.raises(ForbiddenError):
        await handler.handle(command(recipe, repo, actor))
    assert repo.recipes[recipe.id].title == "Pho Bo" and repo.recipes[recipe.id].row_version == 0


@pytest.mark.anyio
async def test_unknown_recipe_is_not_found():
    repo, handler, recipe = make_handler()

    with pytest.raises(NotFoundError):
        await handler.handle(command(recipe, repo, recipe_id=uuid.uuid4()))


@pytest.mark.anyio
async def test_soft_deleted_recipe_is_not_found():
    repo, handler, recipe = make_handler()
    recipe.is_deleted = True

    with pytest.raises(NotFoundError):
        await handler.handle(command(recipe, repo))


@pytest.mark.anyio
async def test_unknown_category_is_unprocessable_and_nothing_is_written():
    repo, handler, recipe = make_handler()

    with pytest.raises(UnprocessableError):
        await handler.handle(command(recipe, repo, category_id=uuid.uuid4()))
    assert repo.recipes[recipe.id].row_version == 0


@pytest.mark.anyio
async def test_forbidden_takes_precedence_over_a_stale_version():
    """A non-owner must not learn anything about the recipe's version."""
    repo, handler, recipe = make_handler()

    with pytest.raises(ForbiddenError):
        await handler.handle(command(recipe, repo, OTHER_AUTHOR, expected_version=99))
