import uuid

import pytest

from culinary_blog.errors import ForbiddenError, NotFoundError
from culinary_blog.recipes.commands.add_step import AddStepCommand, AddStepHandler
from culinary_blog.recipes.commands.delete_step import DeleteStepCommand, DeleteStepHandler
from culinary_blog.recipes.commands.update_step import UpdateStepCommand, UpdateStepHandler
from culinary_blog.recipes.enums import RecipeStatus
from culinary_blog.recipes.schemas import StepIn
from tests.recipes.fakes import ADMIN, AUTHOR, OTHER_AUTHOR, READER, FakeRecipeRepository


def setup():
    repo = FakeRecipeRepository()
    return repo, repo.seed_recipe(AUTHOR, RecipeStatus.DRAFT)


async def add(repo, recipe, actor=AUTHOR, title="Ninh xương", **fields):
    data = StepIn(**({"title": title, "description": "Ninh 3 tiếng"} | fields))
    return await AddStepHandler(repo).handle(AddStepCommand(actor, recipe.id, data))


@pytest.mark.anyio
async def test_steps_are_numbered_sequentially_by_the_server():
    repo, recipe = setup()
    numbers = [(await add(repo, recipe, title=f"Bước {n}")).step_number for n in range(3)]
    assert numbers == [1, 2, 3]


def test_step_in_schema_has_no_step_number_field():
    assert "step_number" not in StepIn.model_fields


@pytest.mark.anyio
async def test_admin_can_add_step_to_someone_elses_recipe():
    repo, recipe = setup()
    assert (await add(repo, recipe, actor=ADMIN)).step_number == 1


@pytest.mark.anyio
@pytest.mark.parametrize("actor", [OTHER_AUTHOR, READER])
async def test_add_forbidden_for_non_owner(actor):
    repo, recipe = setup()
    with pytest.raises(ForbiddenError):
        await add(repo, recipe, actor=actor)
    assert repo.steps == []


@pytest.mark.anyio
async def test_add_to_missing_recipe_is_not_found():
    repo, _ = setup()
    with pytest.raises(NotFoundError):
        await AddStepHandler(repo).handle(AddStepCommand(AUTHOR, uuid.uuid4(), StepIn(title="a", description="b")))


@pytest.mark.parametrize("fields", [{"title": ""}, {"title": "   "}, {"description": ""}, {"description": "x" * 2001}])
def test_schema_rejects_blank_or_oversized_fields(fields):
    with pytest.raises(ValueError):
        StepIn(**({"title": "t", "description": "d"} | fields))


@pytest.mark.anyio
async def test_update_replaces_content_but_never_the_number():
    repo, recipe = setup()
    await add(repo, recipe)
    second = await add(repo, recipe, title="Nêm nếm")
    out = await UpdateStepHandler(repo).handle(
        UpdateStepCommand(
            AUTHOR, recipe.id, second.id, StepIn(title="Nêm gia vị", description="Nêm vừa", duration_minutes=5)
        )
    )

    assert (out.title, out.duration_minutes, out.step_number) == ("Nêm gia vị", 5, 2)


@pytest.mark.anyio
async def test_update_forbidden_and_not_found():
    repo, recipe = setup()
    step = await add(repo, recipe)
    handler = UpdateStepHandler(repo)
    data = StepIn(title="t", description="d")
    with pytest.raises(ForbiddenError):
        await handler.handle(UpdateStepCommand(OTHER_AUTHOR, recipe.id, step.id, data))
    with pytest.raises(NotFoundError):
        await handler.handle(UpdateStepCommand(AUTHOR, recipe.id, uuid.uuid4(), data))


@pytest.mark.anyio
async def test_delete_renumbers_remaining_steps_contiguously():
    repo, recipe = setup()
    first = await add(repo, recipe, title="A")
    await add(repo, recipe, title="B")
    await add(repo, recipe, title="C")

    await DeleteStepHandler(repo).handle(DeleteStepCommand(AUTHOR, recipe.id, first.id))

    steps, _ = await repo.get_children(recipe.id)
    assert [(s.title, s.step_number) for s in steps] == [("B", 1), ("C", 2)]


@pytest.mark.anyio
async def test_new_step_after_delete_continues_from_the_renumbered_tail():
    repo, recipe = setup()
    first = await add(repo, recipe, title="A")
    await add(repo, recipe, title="B")
    await DeleteStepHandler(repo).handle(DeleteStepCommand(AUTHOR, recipe.id, first.id))

    assert (await add(repo, recipe, title="C")).step_number == 2


@pytest.mark.anyio
async def test_delete_forbidden_and_not_found():
    repo, recipe = setup()
    step = await add(repo, recipe)
    handler = DeleteStepHandler(repo)
    with pytest.raises(ForbiddenError):
        await handler.handle(DeleteStepCommand(OTHER_AUTHOR, recipe.id, step.id))
    await handler.handle(DeleteStepCommand(AUTHOR, recipe.id, step.id))
    with pytest.raises(NotFoundError):
        await handler.handle(DeleteStepCommand(AUTHOR, recipe.id, step.id))
