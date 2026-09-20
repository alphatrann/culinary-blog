import pytest

from culinary_blog.auth.commands.register import RegisterCommand, RegisterHandler
from culinary_blog.errors import ConflictError
from tests.auth.fakes import PASSWORD, make_services


def make_handler():
    s = make_services()
    return s, RegisterHandler(s.repository, s.hasher, s.issuer)


@pytest.mark.anyio
async def test_register_creates_author_with_hashed_password_and_refresh_hash():
    s, handler = make_handler()
    session = await handler.handle(RegisterCommand("Cook", "Cook@Example.com", PASSWORD))

    (user,) = s.repository.users.values()
    assert user.email == "cook@example.com"
    assert user.roles == ["author"]
    assert user.password_hash and user.password_hash != PASSWORD
    assert session.user.roles == ["author"]
    # only the hash is persisted, never the raw token
    assert session.refresh_token not in s.repository.tokens
    assert s.tokens.hash_refresh_token(session.refresh_token) in s.repository.tokens
    assert s.tokens.decode_access_token(session.access_token).user_id == user.id


@pytest.mark.anyio
async def test_register_duplicate_email_conflicts():
    _, handler = make_handler()
    await handler.handle(RegisterCommand("Cook", "cook@example.com", PASSWORD))
    with pytest.raises(ConflictError):
        await handler.handle(RegisterCommand("Other", "COOK@example.com", PASSWORD))
