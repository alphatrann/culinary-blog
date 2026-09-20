import uuid
from decimal import Decimal

import pytest

from culinary_blog.errors import ConflictError, ForbiddenError, UnprocessableError
from culinary_blog.recipes.commands.create_recipe import CreateRecipeCommand, CreateRecipeHandler
from culinary_blog.recipes.enums import RecipeDifficulty, RecipeStatus
from culinary_blog.recipes.schemas import IngredientIn, NutritionIn, StepIn
from tests.recipes.fakes import ADMIN, AUTHOR, NO_ROLES, READER, FakeRecipeRepository


def make_handler():
    repo = FakeRecipeRepository()
    return repo, CreateRecipeHandler(repo), repo.add_category()


def command(category_id: uuid.UUID, actor=AUTHOR, title: str = "Phở Bò Hà Nội", **overrides) -> CreateRecipeCommand:
    fields = {
        "description": "Traditional beef noodle soup",
        "prep_time_minutes": 30,
        "cook_time_minutes": 180,
        "servings": 4,
    } | overrides
    return CreateRecipeCommand(actor, title, category_id=category_id, **fields)


@pytest.mark.anyio
async def test_author_creates_draft_owned_by_author_with_generated_slug():
    repo, handler, category_id = make_handler()
    out = await handler.handle(command(category_id, difficulty=RecipeDifficulty.HARD))

    assert out.slug == "pho-bo-ha-noi"
    assert out.status == RecipeStatus.DRAFT and out.published_at is None
    assert out.author_id == AUTHOR.user_id and out.category_id == category_id
    assert out.difficulty == RecipeDifficulty.HARD and out.steps == [] and out.ingredients == []
    (stored,) = repo.recipes.values()
    assert stored.status == RecipeStatus.DRAFT and stored.author_id == AUTHOR.user_id


@pytest.mark.anyio
async def test_admin_can_create():
    _, handler, category_id = make_handler()

    assert (await handler.handle(command(category_id, ADMIN))).author_id == ADMIN.user_id


@pytest.mark.anyio
async def test_slug_clash_gets_numeric_suffix():
    _, handler, category_id = make_handler()
    slugs = [(await handler.handle(command(category_id, title=t))).slug for t in ("Pho Bo", "Phở Bò", "pho-bo!")]

    assert slugs == ["pho-bo", "pho-bo-2", "pho-bo-3"]


@pytest.mark.anyio
async def test_long_title_slug_stays_within_column_with_room_for_suffix():
    _, handler, category_id = make_handler()
    title = "a" * 200
    first = await handler.handle(command(category_id, title=title))
    second = await handler.handle(command(category_id, title=title))

    assert len(first.slug) == 200 and second.slug == f"{'a' * 200}-2"


@pytest.mark.anyio
async def test_unsluggable_title_falls_back_to_recipe():
    _, handler, category_id = make_handler()

    assert (await handler.handle(command(category_id, title="!!!!!"))).slug == "recipe"


@pytest.mark.anyio
async def test_steps_get_server_assigned_contiguous_numbers():
    repo, handler, category_id = make_handler()
    steps = [
        StepIn(title="Boil", description="Boil bones", duration_minutes=60),
        StepIn(title="Serve", description="x"),
    ]
    out = await handler.handle(command(category_id, steps=steps))

    assert [s.step_number for s in out.steps] == [1, 2]
    assert [s.title for s in out.steps] == ["Boil", "Serve"]
    assert {s.recipe_id for s in repo.steps} == {out.id}


@pytest.mark.anyio
async def test_ingredients_default_order_to_position_and_honour_explicit_order():
    repo, handler, category_id = make_handler()
    ingredients = [
        IngredientIn(name="Rice noodles", quantity=Decimal("500"), unit="gram"),
        IngredientIn(name="Salt"),
        IngredientIn(name="Star anise", order_index=7),
    ]
    out = await handler.handle(command(category_id, ingredients=ingredients))

    assert [(i.name, i.order_index) for i in out.ingredients] == [("Rice noodles", 0), ("Salt", 1), ("Star anise", 7)]
    assert out.ingredients[0].quantity == 500 and out.ingredients[1].quantity is None
    assert len(repo.ingredients) == 3


@pytest.mark.anyio
async def test_nutrition_is_stored_on_the_recipe_and_echoed():
    repo, handler, category_id = make_handler()
    out = await handler.handle(
        command(category_id, nutrition=NutritionIn(calories=Decimal("450.5"), fat=Decimal("12")))
    )

    assert out.nutrition.calories == 450.5 and out.nutrition.fat == 12 and out.nutrition.protein is None
    (stored,) = repo.recipes.values()
    assert stored.nutrition_calories == Decimal("450.5") and stored.nutrition_sodium is None


@pytest.mark.anyio
async def test_unknown_category_is_unprocessable_and_nothing_is_written():
    repo, handler, _ = make_handler()

    with pytest.raises(UnprocessableError):
        await handler.handle(command(uuid.uuid4()))
    assert not repo.recipes


@pytest.mark.anyio
@pytest.mark.parametrize("actor", [READER, NO_ROLES])
async def test_caller_without_author_or_admin_role_is_forbidden_and_nothing_is_written(actor):
    repo, handler, category_id = make_handler()

    with pytest.raises(ForbiddenError):
        await handler.handle(command(category_id, actor))
    assert not repo.recipes and not repo.steps


@pytest.mark.anyio
async def test_slug_race_surfaces_as_conflict():
    class RacyRepository(FakeRecipeRepository):
        async def slug_taken(self, slug: str) -> bool:
            return False  # the check passes, then the unique constraint fires on insert

    repo = RacyRepository()
    category_id = repo.add_category()
    handler = CreateRecipeHandler(repo)
    await handler.handle(command(category_id))

    with pytest.raises(ConflictError):
        await handler.handle(command(category_id))
