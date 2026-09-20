import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from culinary_blog.auth.models import User
from culinary_blog.auth.repository import AuthRepository
from culinary_blog.auth.schemas import AuthSession
from culinary_blog.auth.security import PasswordHasher
from culinary_blog.auth.session_issuer import SessionIssuer
from culinary_blog.cqrs import Command, CommandHandler

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RegisterCommand(Command):
    display_name: str
    email: str
    password: str
    client_ip: str | None = None


class RegisterHandler(CommandHandler[RegisterCommand, AuthSession]):
    """FR-AUTH-001: creates an author account and auto-logs it in.

    Duplicate emails are rejected by the unique index (the repository raises ConflictError), not by a racy pre-check.
    """

    def __init__(self, repository: AuthRepository, hasher: PasswordHasher, issuer: SessionIssuer) -> None:
        self._repository = repository
        self._hasher = hasher
        self._issuer = issuer

    async def handle(self, command: RegisterCommand) -> AuthSession:
        email = command.email.lower()
        user = User(
            email=email,
            display_name=command.display_name,
            password_hash=await self._hasher.hash(command.password),
            roles=["author"],
        )
        session, refresh_record = self._issuer.issue(user, command.client_ip)
        await self._repository.create_user_with_refresh_token(user, refresh_record)
        logger.info("user registered", extra={"user_id": str(user.id), "at": datetime.now(UTC).isoformat()})
        return session
