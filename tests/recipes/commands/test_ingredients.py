import uuid
from decimal import Decimal

import pytest

from culinary_blog.errors import ForbiddenError, NotFoundError
from culinary_blog.recipes.commands.add_ingredient import AddIngredientCommand, AddIngredientHandler
from culinary_blog.recipes.commands.delete_ingredient import DeleteIngredientCommand, DeleteIngredientHandler
from culinary_blog.recipes.commands.update_ingredient import UpdateIngredientCommand, UpdateIngredientHandler
from culinary_blog.recipes.enums import RecipeStatus
from culinary_blog.recipes.schemas import IngredientIn
from tests.recipes.fakes import ADMIN, AUTHOR, NO_ROLES, OTHER_AUTHOR, READER, FakeRecipeRepository


def setup():
    repo = FakeRecipeRepository()
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT)
    return repo, recipe


async def add(repo, recipe, actor=AUTHOR, **fields):
    data = IngredientIn(**({"name": "Muối"} | fields))
    return await AddIngredientHandler(repo).handle(AddIngredientCommand(actor, recipe.id, data))


@pytest.mark.anyio
async def test_owner_adds_ingredient_appended_after_existing_ones():
    repo, recipe = setup()
    first = await add(repo, recipe, name="Thịt bò", quantity=Decimal("500"), unit="g")
    second = await add(repo, recipe, name="Muối")

    assert (first.order_index, second.order_index) == (0, 1)
    assert first.quantity == 500 and second.quantity is None and second.unit is None


@pytest.mark.anyio
async def test_explicit_order_index_is_respected():
    repo, recipe = setup()
    out = await add(repo, recipe, order_index=7)
    assert out.order_index == 7


@pytest.mark.anyio
async def test_admin_can_add_to_someone_elses_recipe():
    repo, recipe = setup()
    assert (await add(repo, recipe, actor=ADMIN)).name == "Muối"


@pytest.mark.anyio
@pytest.mark.parametrize("actor", [OTHER_AUTHOR, READER, NO_ROLES])
async def test_add_forbidden_for_non_owner(actor):
    repo, recipe = setup()
    with pytest.raises(ForbiddenError):
        await add(repo, recipe, actor=actor)
    assert repo.ingredients == []


@pytest.mark.anyio
async def test_add_to_missing_or_deleted_recipe_is_not_found():
    repo, recipe = setup()
    handler = AddIngredientHandler(repo)
    data = IngredientIn(name="Muối")
    with pytest.raises(NotFoundError):
        await handler.handle(AddIngredientCommand(AUTHOR, uuid.uuid4(), data))
    recipe.is_deleted = True
    with pytest.raises(NotFoundError):
        await handler.handle(AddIngredientCommand(AUTHOR, recipe.id, data))


@pytest.mark.anyio
async def test_update_replaces_fields_and_keeps_order_when_omitted():
    repo, recipe = setup()
    created = await add(repo, recipe, name="Hành", order_index=3)
    out = await UpdateIngredientHandler(repo).handle(
        UpdateIngredientCommand(
            AUTHOR, recipe.id, created.id, IngredientIn(name="Hành lá", quantity=Decimal("2.5"), unit="củ")
        )
    )

    assert (out.name, out.quantity, out.unit, out.order_index) == ("Hành lá", 2.5, "củ", 3)


@pytest.mark.anyio
async def test_update_can_clear_quantity_and_unit_together():
    repo, recipe = setup()
    created = await add(repo, recipe, name="Hành", quantity=Decimal("1"), unit="củ")
    out = await UpdateIngredientHandler(repo).handle(
        UpdateIngredientCommand(AUTHOR, recipe.id, created.id, IngredientIn(name="Hành"))
    )
    assert out.quantity is None and out.unit is None


@pytest.mark.anyio
async def test_update_forbidden_and_not_found():
    repo, recipe = setup()
    created = await add(repo, recipe)
    handler = UpdateIngredientHandler(repo)
    data = IngredientIn(name="X")
    with pytest.raises(ForbiddenError):
        await handler.handle(UpdateIngredientCommand(OTHER_AUTHOR, recipe.id, created.id, data))
    with pytest.raises(NotFoundError):
        await handler.handle(UpdateIngredientCommand(AUTHOR, recipe.id, uuid.uuid4(), data))


@pytest.mark.anyio
async def test_ingredient_of_another_recipe_is_not_found():
    repo, recipe = setup()
    other = repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT, title="Bun Cha")
    created = await add(repo, other)
    with pytest.raises(NotFoundError):
        await UpdateIngredientHandler(repo).handle(
            UpdateIngredientCommand(AUTHOR, recipe.id, created.id, IngredientIn(name="X"))
        )


@pytest.mark.anyio
async def test_delete_soft_deletes_and_second_delete_is_not_found():
    repo, recipe = setup()
    created = await add(repo, recipe)
    handler = DeleteIngredientHandler(repo)
    await handler.handle(DeleteIngredientCommand(AUTHOR, recipe.id, created.id))

    assert repo.ingredients[0].is_deleted is True
    with pytest.raises(NotFoundError):
        await handler.handle(DeleteIngredientCommand(AUTHOR, recipe.id, created.id))


@pytest.mark.anyio
async def test_delete_forbidden_for_non_owner():
    repo, recipe = setup()
    created = await add(repo, recipe)
    with pytest.raises(ForbiddenError):
        await DeleteIngredientHandler(repo).handle(DeleteIngredientCommand(OTHER_AUTHOR, recipe.id, created.id))
    assert repo.ingredients[0].is_deleted is False


@pytest.mark.parametrize("fields", [{"quantity": Decimal("1")}, {"unit": "g"}, {"quantity": Decimal("0"), "unit": "g"}])
def test_schema_rejects_broken_quantity_unit_pairs(fields):
    with pytest.raises(ValueError):
        IngredientIn(name="Muối", **fields)
