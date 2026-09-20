from datetime import UTC, datetime, timedelta

import pytest

from culinary_blog.auth.commands.login import LoginCommand, LoginHandler
from culinary_blog.errors import LockedError, UnauthorizedError
from tests.auth.fakes import PASSWORD, add_user, make_services

EMAIL = "cook@example.com"


def make_handler(max_failed: int = 3):
    s = make_services()
    return s, LoginHandler(s.repository, s.hasher, s.issuer, max_failed, timedelta(minutes=15))


@pytest.mark.anyio
async def test_login_success_issues_tokens_and_resets_failures():
    s, handler = make_handler()
    user = await add_user(s, failed_login_count=2)
    session = await handler.handle(LoginCommand(EMAIL, PASSWORD))

    assert user.failed_login_count == 0
    assert s.tokens.hash_refresh_token(session.refresh_token) in s.repository.tokens


@pytest.mark.anyio
async def test_wrong_password_and_unknown_email_give_same_error():
    s, handler = make_handler()
    await add_user(s)
    with pytest.raises(UnauthorizedError) as wrong:
        await handler.handle(LoginCommand(EMAIL, "Wrong!Pass1"))
    with pytest.raises(UnauthorizedError) as unknown:
        await handler.handle(LoginCommand("nobody@example.com", PASSWORD))
    assert wrong.value.detail == unknown.value.detail


@pytest.mark.anyio
async def test_repeated_failures_lock_account_even_for_correct_password():
    s, handler = make_handler(max_failed=3)
    user = await add_user(s)
    for _ in range(3):
        with pytest.raises(UnauthorizedError):
            await handler.handle(LoginCommand(EMAIL, "Wrong!Pass1"))

    assert user.locked_until and user.locked_until > datetime.now(UTC)
    with pytest.raises(LockedError):
        await handler.handle(LoginCommand(EMAIL, PASSWORD))


@pytest.mark.anyio
async def test_expired_lock_allows_login():
    s, handler = make_handler()
    await add_user(s, locked_until=datetime.now(UTC) - timedelta(minutes=1))
    await handler.handle(LoginCommand(EMAIL, PASSWORD))


@pytest.mark.anyio
async def test_inactive_user_cannot_log_in():
    s, handler = make_handler()
    await add_user(s, is_active=False)
    with pytest.raises(UnauthorizedError):
        await handler.handle(LoginCommand(EMAIL, PASSWORD))
