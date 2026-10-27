import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from culinary_blog.auth.google import GoogleIdTokenVerifier, GoogleProfile
from culinary_blog.auth.models import RefreshToken, User
from culinary_blog.auth.repository import AuthRepository
from culinary_blog.auth.security import PasswordHasher, TokenService
from culinary_blog.auth.session_issuer import SessionIssuer
from culinary_blog.errors import ConflictError, UnauthorizedError
from tests.recipes.fakes import FakeJobQueue

PASSWORD = "Str0ng!Pass"


class FakeAuthRepository(AuthRepository):
    """In-memory stand-in mirroring the real repository's atomic-revoke semantics."""

    def __init__(self) -> None:  # deliberately skips super().__init__: no database
        self.users: dict[uuid.UUID, User] = {}
        self.tokens: dict[str, RefreshToken] = {}

    async def get_user_by_email(self, email: str) -> User | None:
        return next((u for u in self.users.values() if u.email == email and not u.is_deleted), None)

    async def get_user_by_google_sub(self, google_sub: str) -> User | None:
        return next((u for u in self.users.values() if u.google_sub == google_sub and not u.is_deleted), None)

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        user = self.users.get(user_id)
        return user if user and not user.is_deleted else None

    async def update_profile(self, user_id: uuid.UUID, values: dict[str, object]) -> User | None:
        user = await self.get_user_by_id(user_id)
        if user is None or not user.is_active:
            return None
        for name, value in values.items():
            setattr(user, name, value)
        user.row_version += 1
        return user

    async def create_user_with_refresh_token(self, user: User, token: RefreshToken) -> None:
        if await self.get_user_by_email(user.email):
            raise ConflictError("Email is already registered")
        self.users[user.id] = user
        self.tokens[token.token_hash] = token

    async def save_login_state(self, user: User) -> None:
        self.users[user.id] = user

    async def add_refresh_token(self, token: RefreshToken) -> None:
        self.tokens[token.token_hash] = token

    async def get_refresh_token(self, token_hash: str) -> RefreshToken | None:
        return self.tokens.get(token_hash)

    async def rotate_refresh_token(self, old_hash: str, new_token: RefreshToken) -> bool:
        old = self.tokens.get(old_hash)
        if old is None or old.revoked_at is not None:
            return False
        old.revoked_at = datetime.now(UTC)
        old.replaced_by_token_hash = new_token.token_hash
        self.tokens[new_token.token_hash] = new_token
        return True

    async def revoke_refresh_token(self, token_hash: str) -> None:
        token = self.tokens.get(token_hash)
        if token and token.revoked_at is None:
            token.revoked_at = datetime.now(UTC)

    async def revoke_all_refresh_tokens(self, user_id: uuid.UUID) -> None:
        for token in self.tokens.values():
            if token.user_id == user_id and token.revoked_at is None:
                token.revoked_at = datetime.now(UTC)


class FakeGoogleVerifier(GoogleIdTokenVerifier):
    """Maps a token string to a profile; any unknown token is rejected like a bad signature would be."""

    def __init__(self) -> None:  # deliberately skips super().__init__: no HTTP client
        self.profiles: dict[str, GoogleProfile] = {}

    async def verify(self, token: str) -> GoogleProfile:
        if token not in self.profiles:
            raise UnauthorizedError("Invalid Google ID token")
        return self.profiles[token]


@dataclass
class Services:
    repository: FakeAuthRepository
    hasher: PasswordHasher
    tokens: TokenService
    issuer: SessionIssuer
    google: FakeGoogleVerifier
    queue: FakeJobQueue


def make_services() -> Services:
    tokens = TokenService("test-secret-key-at-least-32-bytes-long", timedelta(minutes=15), timedelta(days=7))
    return Services(
        FakeAuthRepository(), PasswordHasher(), tokens, SessionIssuer(tokens), FakeGoogleVerifier(), FakeJobQueue()
    )


async def add_user(services: Services, email: str = "cook@example.com", **overrides: object) -> User:
    user = User(
        email=email,
        display_name="Cook",
        password_hash=await services.hasher.hash(PASSWORD),
        roles=["author"],
        **overrides,  # type: ignore[arg-type]
    )
    services.repository.users[user.id] = user
    return user
