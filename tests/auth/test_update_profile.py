import pytest

from culinary_blog.auth.commands.update_profile import UpdateProfileCommand, UpdateProfileHandler
from culinary_blog.auth.principal import Principal
from culinary_blog.errors import UnauthorizedError
from tests.auth.fakes import add_user, make_services


@pytest.mark.anyio
async def test_only_supplied_fields_change_and_row_version_is_bumped():
    s = make_services()
    user = await add_user(s, bio="old")

    out = await UpdateProfileHandler(s.repository).handle(
        UpdateProfileCommand(Principal(user.id, ("author",)), {"bio": "new"})
    )

    assert out.bio == "new" and out.display_name == "Cook"
    assert user.row_version == 1


@pytest.mark.anyio
async def test_missing_or_inactive_account_is_unauthorized():
    s = make_services()
    user = await add_user(s, is_active=False)

    with pytest.raises(UnauthorizedError):
        await UpdateProfileHandler(s.repository).handle(
            UpdateProfileCommand(Principal(user.id, ("author",)), {"bio": "new"})
        )
