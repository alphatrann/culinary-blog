from datetime import UTC, datetime, timedelta

import pytest

from culinary_blog.auth.commands.login import LoginCommand, LoginHandler
from culinary_blog.auth.commands.refresh import RefreshCommand, RefreshHandler
from culinary_blog.errors import UnauthorizedError
from tests.auth.fakes import PASSWORD, add_user, make_services


async def logged_in():
    s = make_services()
    await add_user(s)
    login = LoginHandler(s.repository, s.hasher, s.issuer, 5, timedelta(minutes=15))
    session = await login.handle(LoginCommand("cook@example.com", PASSWORD))
    return s, RefreshHandler(s.repository, s.tokens, s.issuer), session


@pytest.mark.anyio
async def test_refresh_rotates_token():
    s, handler, first = await logged_in()
    second = await handler.handle(RefreshCommand(first.refresh_token))

    assert second.refresh_token != first.refresh_token
    old = s.repository.tokens[s.tokens.hash_refresh_token(first.refresh_token)]
    assert old.revoked_at is not None
    assert old.replaced_by_token_hash == s.tokens.hash_refresh_token(second.refresh_token)
    await handler.handle(RefreshCommand(second.refresh_token))  # the new one is usable


@pytest.mark.anyio
async def test_reusing_rotated_token_is_rejected_and_revokes_the_whole_family():
    s, handler, first = await logged_in()
    second = await handler.handle(RefreshCommand(first.refresh_token))

    with pytest.raises(UnauthorizedError):
        await handler.handle(RefreshCommand(first.refresh_token))
    assert all(t.revoked_at is not None for t in s.repository.tokens.values())
    with pytest.raises(UnauthorizedError):  # the legitimately issued successor is dead too
        await handler.handle(RefreshCommand(second.refresh_token))


@pytest.mark.anyio
async def test_unknown_token_rejected():
    _, handler, _ = await logged_in()
    with pytest.raises(UnauthorizedError):
        await handler.handle(RefreshCommand("not-a-real-token"))


@pytest.mark.anyio
async def test_expired_token_rejected():
    s, handler, first = await logged_in()
    stored = s.repository.tokens[s.tokens.hash_refresh_token(first.refresh_token)]
    stored.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    with pytest.raises(UnauthorizedError):
        await handler.handle(RefreshCommand(first.refresh_token))


@pytest.mark.anyio
async def test_deactivated_user_rejected():
    s, handler, first = await logged_in()
    next(iter(s.repository.users.values())).is_active = False
    with pytest.raises(UnauthorizedError):
        await handler.handle(RefreshCommand(first.refresh_token))
