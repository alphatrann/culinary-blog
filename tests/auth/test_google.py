import json
import time
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from culinary_blog.auth.google import GoogleIdTokenVerifier
from culinary_blog.errors import ServiceUnavailableError, UnauthorizedError

CLIENT_ID = "test-client.apps.googleusercontent.com"
KID = "test-key"
PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)


class FakeCertTransport:
    """Stands in for google-auth's HTTP transport: serves one JWK set for Google's cert URL, no network."""

    def __init__(self, status: int = 200) -> None:
        self.status = status

    def __call__(self, url, method="GET", **_: object):
        jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(PRIVATE_KEY.public_key()))
        jwk.update({"kid": KID, "alg": "RS256", "use": "sig"})
        body = json.dumps({"keys": [jwk]}).encode()
        return SimpleNamespace(status=self.status, data=body)


def sign(**overrides: object) -> str:
    now = int(time.time())
    claims = {
        "iss": "https://accounts.google.com",
        "aud": CLIENT_ID,
        "sub": "g-123",
        "email": "cook@example.com",
        "email_verified": True,
        "name": "Cook",
        "picture": "https://example.com/a.png",
        "iat": now,
        "exp": now + 300,
        **overrides,
    }
    return jwt.encode(claims, PRIVATE_KEY, algorithm="RS256", headers={"kid": KID})


def verifier(transport: FakeCertTransport | None = None) -> GoogleIdTokenVerifier:
    return GoogleIdTokenVerifier(CLIENT_ID, transport or FakeCertTransport())


@pytest.mark.anyio
async def test_valid_token_yields_profile_from_claims():
    profile = await verifier().verify(sign())

    assert (profile.sub, profile.email, profile.email_verified) == ("g-123", "cook@example.com", True)
    assert (profile.name, profile.picture) == ("Cook", "https://example.com/a.png")


@pytest.mark.anyio
@pytest.mark.parametrize(
    "token",
    [
        sign(aud="someone-else.apps.googleusercontent.com"),
        sign(iss="https://evil.example.com"),
        sign(exp=int(time.time()) - 600),
        sign()[:-4] + "AAAA",  # broken signature
    ],
    ids=["wrong-aud", "wrong-iss", "expired", "bad-signature"],
)
async def test_invalid_tokens_are_401(token):
    with pytest.raises(UnauthorizedError):
        await verifier().verify(token)


@pytest.mark.anyio
async def test_unreachable_google_certs_are_503():
    with pytest.raises(ServiceUnavailableError):
        await verifier(FakeCertTransport(status=500)).verify(sign())


@pytest.mark.anyio
async def test_empty_client_id_means_not_configured_503():
    with pytest.raises(ServiceUnavailableError):
        await GoogleIdTokenVerifier("", FakeCertTransport()).verify(sign())
