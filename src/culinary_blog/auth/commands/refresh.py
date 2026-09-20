import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import NoReturn

from culinary_blog.auth.repository import AuthRepository
from culinary_blog.auth.schemas import AuthSession
from culinary_blog.auth.security import TokenService
from culinary_blog.auth.session_issuer import SessionIssuer
from culinary_blog.cqrs import Command, CommandHandler
from culinary_blog.errors import UnauthorizedError

logger = logging.getLogger(__name__)

INVALID_REFRESH = "Invalid refresh token"


@dataclass(frozen=True)
class RefreshCommand(Command):
    refresh_token: str
    client_ip: str | None = None


class RefreshHandler(CommandHandler[RefreshCommand, AuthSession]):
    """FR-AUTH-004: rotates the refresh token on every use; presenting a revoked one is treated as theft."""

    def __init__(self, repository: AuthRepository, tokens: TokenService, issuer: SessionIssuer) -> None:
        self._repository = repository
        self._tokens = tokens
        self._issuer = issuer

    async def handle(self, command: RefreshCommand) -> AuthSession:
        old_hash = self._tokens.hash_refresh_token(command.refresh_token)
        stored = await self._repository.get_refresh_token(old_hash)
        if stored is None:
            raise UnauthorizedError(INVALID_REFRESH)
        if stored.revoked_at is not None:
            await self._reject_reuse(stored.user_id)
        if stored.expires_at <= datetime.now(UTC):
            raise UnauthorizedError(INVALID_REFRESH)

        user = await self._repository.get_user_by_id(stored.user_id)
        if user is None or not user.is_active:
            raise UnauthorizedError(INVALID_REFRESH)

        session, new_record = self._issuer.issue(user, command.client_ip)
        if not await self._repository.rotate_refresh_token(old_hash, new_record):
            await self._reject_reuse(user.id)  # lost a race with a concurrent use of the same token
        logger.info("refresh token rotated", extra={"user_id": str(user.id), "at": datetime.now(UTC).isoformat()})
        return session

    async def _reject_reuse(self, user_id: uuid.UUID) -> NoReturn:
        logger.warning("SECURITY ALERT: revoked refresh token reused", extra={"user_id": str(user_id)})
        await self._repository.revoke_all_refresh_tokens(user_id)
        raise UnauthorizedError(INVALID_REFRESH)
