import asyncio
from dataclasses import dataclass

import jwt
from google.auth.exceptions import GoogleAuthError, TransportError
from google.auth.transport.requests import Request
from google.oauth2 import id_token

from culinary_blog.errors import ServiceUnavailableError, UnauthorizedError


@dataclass(frozen=True)
class GoogleProfile:
    sub: str
    email: str | None
    email_verified: bool
    name: str | None
    picture: str | None


class GoogleIdTokenVerifier:
    """Verifies a Google Identity Services ID token (signature, aud, iss, exp) and maps its claims to a profile."""

    def __init__(self, client_id: str, request: Request | None = None) -> None:
        self._client_id = client_id
        self._request = request or Request()

    async def verify(self, token: str) -> GoogleProfile:
        if not self._client_id:
            raise ServiceUnavailableError("Google sign-in is not configured")
        try:
            # shortcut: fetches Google's certs on every sign-in (no cache), add one if login latency matters
            claims = await asyncio.to_thread(id_token.verify_oauth2_token, token, self._request, self._client_id)
        except TransportError as exc:
            raise ServiceUnavailableError("Google sign-in is temporarily unavailable") from exc
        except (ValueError, GoogleAuthError, jwt.PyJWTError) as exc:  # bad signature, aud, iss or expiry
            raise UnauthorizedError("Invalid Google ID token") from exc
        return GoogleProfile(
            sub=claims["sub"],
            email=claims.get("email"),
            email_verified=bool(claims.get("email_verified")),
            name=claims.get("name"),
            picture=claims.get("picture"),
        )
