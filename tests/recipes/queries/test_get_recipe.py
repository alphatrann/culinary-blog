import pytest

from culinary_blog.errors import ForbiddenError, NotFoundError
from culinary_blog.recipes.enums import RecipeStatus
from culinary_blog.recipes.models import RecipeImage, RecipeIngredient, RecipeStep
from culinary_blog.recipes.queries.get_recipe import GetRecipeHandler, GetRecipeQuery
from tests.recipes.fakes import ADMIN, AUTHOR, OTHER_AUTHOR, FakeRecipeRepository


def make_handler():
    repo = FakeRecipeRepository()
    return repo, GetRecipeHandler(repo)


@pytest.mark.anyio
async def test_guest_sees_published_recipe_with_everything_attached():
    repo, handler = make_handler()
    category_id = repo.add_category("Soups")
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED, category_id=category_id, nutrition_fat="9.5")
    repo.add_user(AUTHOR, "Chef Mai")
    repo.steps += [
        RecipeStep(recipe_id=recipe.id, step_number=2, title="Serve", description="x"),
        RecipeStep(recipe_id=recipe.id, step_number=1, title="Boil", description="x"),
    ]
    repo.ingredients += [
        RecipeIngredient(recipe_id=recipe.id, name="Salt", order_index=1),
        RecipeIngredient(recipe_id=recipe.id, name="Noodles", order_index=0),
    ]
    repo.images.append(RecipeImage(recipe_id=recipe.id, original_url="https://x/a.jpg", is_primary=True))

    out = await handler.handle(GetRecipeQuery(recipe.slug))

    assert out.slug == recipe.slug and out.row_version == 0
    assert [s.title for s in out.steps] == ["Boil", "Serve"]  # by step_number
    assert [i.name for i in out.ingredients] == ["Noodles", "Salt"]  # by order_index
    assert [(i.original_url, i.is_primary) for i in out.images] == [("https://x/a.jpg", True)]
    assert (out.category.id, out.category.name, out.category.slug) == (category_id, "Soups", "soups")
    assert (out.author.id, out.author.display_name) == (AUTHOR.user_id, "Chef Mai")
    assert out.nutrition.fat == 9.5


@pytest.mark.anyio
async def test_author_block_never_exposes_private_fields():
    repo, handler = make_handler()
    recipe = repo.seed_recipe(AUTHOR)
    out = await handler.handle(GetRecipeQuery(recipe.slug))

    assert set(out.author.model_dump()) == {"id", "display_name", "avatar_url"}


@pytest.mark.anyio
async def test_unknown_slug_is_not_found():
    _, handler = make_handler()

    with pytest.raises(NotFoundError):
        await handler.handle(GetRecipeQuery("nope"))


@pytest.mark.anyio
async def test_soft_deleted_recipe_is_not_found():
    repo, handler = make_handler()
    recipe = repo.seed_recipe(AUTHOR)
    recipe.is_deleted = True

    with pytest.raises(NotFoundError):
        await handler.handle(GetRecipeQuery(recipe.slug, AUTHOR))


@pytest.mark.anyio
@pytest.mark.parametrize("status", [RecipeStatus.DRAFT, RecipeStatus.ARCHIVED])
@pytest.mark.parametrize("viewer", [None, OTHER_AUTHOR])
async def test_unpublished_recipe_is_forbidden_to_guests_and_other_authors(status, viewer):
    repo, handler = make_handler()
    recipe = repo.seed_recipe(AUTHOR, status)

    with pytest.raises(ForbiddenError):
        await handler.handle(GetRecipeQuery(recipe.slug, viewer))


@pytest.mark.anyio
@pytest.mark.parametrize("status", [RecipeStatus.DRAFT, RecipeStatus.ARCHIVED])
@pytest.mark.parametrize("viewer", [AUTHOR, ADMIN])
async def test_unpublished_recipe_is_visible_to_owner_and_admin(status, viewer):
    repo, handler = make_handler()
    recipe = repo.seed_recipe(AUTHOR, status)

    assert (await handler.handle(GetRecipeQuery(recipe.slug, viewer))).status == status


@pytest.mark.anyio
async def test_other_authors_can_view_a_published_recipe():
    repo, handler = make_handler()
    recipe = repo.seed_recipe(AUTHOR, RecipeStatus.PUBLISHED)

    assert (await handler.handle(GetRecipeQuery(recipe.slug, OTHER_AUTHOR))).id == recipe.id
