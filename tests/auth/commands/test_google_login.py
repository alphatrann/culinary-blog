from datetime import UTC, datetime, timedelta

import pytest

from culinary_blog.auth.commands.google_login import GoogleLoginCommand, GoogleLoginHandler
from culinary_blog.auth.google import GoogleProfile
from culinary_blog.errors import BadRequestError, LockedError, UnauthorizedError
from tests.auth.fakes import add_user, make_services

PROFILE = GoogleProfile(sub="g-123", email="Cook@Example.com", email_verified=True, name="Cook G", picture=None)


def make_handler():
    s = make_services()
    return s, GoogleLoginHandler(s.repository, s.google, s.issuer)


def use(s, profile: GoogleProfile, token: str = "tok") -> GoogleLoginCommand:
    s.google.profiles[token] = profile
    return GoogleLoginCommand(token)


@pytest.mark.anyio
async def test_new_google_user_is_created_as_author_without_password():
    s, handler = make_handler()
    session = await handler.handle(use(s, PROFILE))

    (user,) = s.repository.users.values()
    assert user.email == "cook@example.com" and user.google_sub == "g-123"
    assert user.password_hash is None and user.roles == ["author"] and user.email_confirmed
    assert user.display_name == "Cook G"
    assert s.tokens.hash_refresh_token(session.refresh_token) in s.repository.tokens


@pytest.mark.anyio
async def test_missing_display_name_falls_back_to_email_local_part():
    s, handler = make_handler()
    await handler.handle(use(s, GoogleProfile("g-1", "jo@example.com", True, None, None)))

    (user,) = s.repository.users.values()
    assert user.display_name == "jo"


@pytest.mark.anyio
async def test_oversized_picture_is_dropped_instead_of_failing_the_insert():
    s, handler = make_handler()
    await handler.handle(use(s, GoogleProfile("g-1", "jo@example.com", True, "Jo", "https://x/" + "a" * 500)))

    (user,) = s.repository.users.values()
    assert user.avatar_url is None


@pytest.mark.anyio
async def test_known_google_sub_logs_in_existing_user():
    s, handler = make_handler()
    user = await add_user(s, google_sub="g-123")
    await handler.handle(use(s, PROFILE))

    assert len(s.repository.users) == 1
    assert s.repository.users[user.id].google_sub == "g-123"


@pytest.mark.anyio
async def test_email_match_links_google_sub_onto_password_account():
    s, handler = make_handler()
    user = await add_user(s)
    session = await handler.handle(use(s, PROFILE))

    assert user.google_sub == "g-123" and user.password_hash is not None
    assert len(s.repository.users) == 1
    assert s.tokens.hash_refresh_token(session.refresh_token) in s.repository.tokens


@pytest.mark.anyio
async def test_unverified_google_email_cannot_take_over_existing_account():
    s, handler = make_handler()
    user = await add_user(s)
    unverified = GoogleProfile("g-evil", "cook@example.com", False, None, None)
    with pytest.raises(UnauthorizedError):
        await handler.handle(use(s, unverified))

    assert user.google_sub is None


@pytest.mark.anyio
async def test_profile_without_email_is_400():
    s, handler = make_handler()
    with pytest.raises(BadRequestError):
        await handler.handle(use(s, GoogleProfile("g-1", None, True, "Jo", None)))


@pytest.mark.anyio
async def test_invalid_token_is_401_and_creates_nothing():
    s, handler = make_handler()
    with pytest.raises(UnauthorizedError):
        await handler.handle(GoogleLoginCommand("forged"))

    assert not s.repository.users


@pytest.mark.anyio
async def test_inactive_account_is_rejected():
    s, handler = make_handler()
    await add_user(s, is_active=False)
    with pytest.raises(UnauthorizedError):
        await handler.handle(use(s, PROFILE))


@pytest.mark.anyio
async def test_locked_account_is_rejected_even_with_valid_google_token():
    s, handler = make_handler()
    await add_user(s, locked_until=datetime.now(UTC) + timedelta(minutes=5))
    with pytest.raises(LockedError):
        await handler.handle(use(s, PROFILE))
