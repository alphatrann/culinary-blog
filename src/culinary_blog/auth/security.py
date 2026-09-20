import asyncio
import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext

from culinary_blog.auth.principal import Principal
from culinary_blog.errors import UnauthorizedError


class PasswordHasher:
    """Argon2id via passlib (CONS-004). Hashing is CPU-bound, so it runs off the event loop."""

    def __init__(self) -> None:
        self._context = CryptContext(schemes=["argon2"], deprecated="auto")
        # Verified against when the account doesn't exist, so login timing doesn't reveal which emails are registered.
        self._dummy_hash = self._context.hash(secrets.token_urlsafe(16))

    async def hash(self, password: str) -> str:
        return await asyncio.to_thread(self._context.hash, password)

    async def verify(self, password: str, password_hash: str | None) -> bool:
        matches = await asyncio.to_thread(self._context.verify, password, password_hash or self._dummy_hash)
        return matches and password_hash is not None


class TokenService:
    """Issues and verifies access JWTs (HS256) and opaque 512-bit refresh tokens."""

    def __init__(self, secret_key: str, access_ttl: timedelta, refresh_ttl: timedelta) -> None:
        self._secret_key = secret_key
        self.access_ttl = access_ttl
        self.refresh_ttl = refresh_ttl

    def create_access_token(self, user_id: uuid.UUID, roles: list[str]) -> str:
        now = datetime.now(UTC)
        claims = {"sub": str(user_id), "roles": roles, "iat": now, "exp": now + self.access_ttl}
        return jwt.encode(claims, self._secret_key, algorithm="HS256")

    def decode_access_token(self, token: str) -> Principal:
        try:
            claims = jwt.decode(token, self._secret_key, algorithms=["HS256"], options={"require": ["exp", "sub"]})
            return Principal(user_id=uuid.UUID(claims["sub"]), roles=tuple(claims.get("roles", [])))
        except (jwt.InvalidTokenError, ValueError, TypeError) as exc:
            raise UnauthorizedError("Invalid or expired access token") from exc

    @staticmethod
    def generate_refresh_token() -> str:
        return secrets.token_urlsafe(64)  # 64 random bytes = 512 bits

    @staticmethod
    def hash_refresh_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def refresh_expiry(self) -> datetime:
        return datetime.now(UTC) + self.refresh_ttl
