import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from culinary_blog.auth.principal import Principal
from culinary_blog.auth.repository import AuthRepository
from culinary_blog.auth.security import TokenService
from culinary_blog.cqrs import Command, CommandHandler

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LogoutCommand(Command):
    actor: Principal
    refresh_token: str | None


class LogoutHandler(CommandHandler[LogoutCommand, None]):
    """FR-AUTH-005: revokes the caller's current refresh token. Idempotent when the token is missing/unknown."""

    def __init__(self, repository: AuthRepository, tokens: TokenService) -> None:
        self._repository = repository
        self._tokens = tokens

    async def handle(self, command: LogoutCommand) -> None:
        if command.refresh_token:
            await self._repository.revoke_refresh_token(self._tokens.hash_refresh_token(command.refresh_token))
        logger.info(
            "user logged out", extra={"user_id": str(command.actor.user_id), "at": datetime.now(UTC).isoformat()}
        )
