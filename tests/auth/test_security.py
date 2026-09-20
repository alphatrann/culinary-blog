import base64
import uuid
from datetime import timedelta

import jwt
import pytest

from culinary_blog.auth.security import PasswordHasher, TokenService
from culinary_blog.errors import UnauthorizedError

SECRET = "test-secret-key-at-least-32-bytes-long"


def make_tokens(access_ttl: timedelta = timedelta(minutes=15)) -> TokenService:
    return TokenService(SECRET, access_ttl, timedelta(days=7))


@pytest.mark.anyio
async def test_password_is_hashed_with_argon2_and_verifies():
    hasher = PasswordHasher()
    hashed = await hasher.hash("Str0ng!Pass")
    assert hashed.startswith("$argon2id$")
    assert await hasher.verify("Str0ng!Pass", hashed)
    assert not await hasher.verify("wrong", hashed)


@pytest.mark.anyio
async def test_verify_without_stored_hash_is_always_false():
    assert not await PasswordHasher().verify("anything", None)


def test_access_token_round_trip():
    tokens, user_id = make_tokens(), uuid.uuid4()
    principal = tokens.decode_access_token(tokens.create_access_token(user_id, ["admin"]))
    assert principal.user_id == user_id
    assert principal.is_admin


def test_expired_access_token_rejected():
    tokens = make_tokens(access_ttl=timedelta(seconds=-1))
    with pytest.raises(UnauthorizedError):
        tokens.decode_access_token(tokens.create_access_token(uuid.uuid4(), []))


def test_tampered_or_foreign_access_token_rejected():
    forged = jwt.encode({"sub": str(uuid.uuid4()), "exp": 9999999999}, "another-secret-key-32-bytes-long!!", "HS256")
    with pytest.raises(UnauthorizedError):
        make_tokens().decode_access_token(forged)
    with pytest.raises(UnauthorizedError):
        make_tokens().decode_access_token("not-a-jwt")


def test_refresh_token_has_512_bits_and_is_stored_as_sha256():
    token = TokenService.generate_refresh_token()
    assert len(base64.urlsafe_b64decode(token + "=" * (-len(token) % 4))) == 64
    assert TokenService.generate_refresh_token() != token
    digest = TokenService.hash_refresh_token(token)
    assert len(digest) == 64 and digest != token
