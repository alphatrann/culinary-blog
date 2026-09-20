import pytest

from culinary_blog.auth.commands.logout import LogoutCommand, LogoutHandler
from culinary_blog.auth.principal import Principal
from tests.auth.fakes import add_user, make_services


@pytest.mark.anyio
async def test_logout_revokes_only_the_presented_refresh_token():
    s = make_services()
    user = await add_user(s)
    current, current_record = s.issuer.issue(user, None)
    _, other_record = s.issuer.issue(user, None)  # e.g. a session on another device
    await s.repository.add_refresh_token(current_record)
    await s.repository.add_refresh_token(other_record)

    await LogoutHandler(s.repository, s.tokens).handle(
        LogoutCommand(Principal(user.id, ("author",)), current.refresh_token)
    )

    assert s.repository.tokens[current_record.token_hash].revoked_at is not None
    assert s.repository.tokens[other_record.token_hash].revoked_at is None


@pytest.mark.anyio
@pytest.mark.parametrize("token", [None, "", "never-issued"])
async def test_logout_is_idempotent_for_missing_or_unknown_token(token):
    s = make_services()
    user = await add_user(s)
    await LogoutHandler(s.repository, s.tokens).handle(LogoutCommand(Principal(user.id, ("author",)), token))
