import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from culinary_blog.auth.principal import Principal
from culinary_blog.auth.repository import AuthRepository
from culinary_blog.auth.schemas import UserOut
from culinary_blog.cqrs import Command, CommandHandler
from culinary_blog.errors import UnauthorizedError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UpdateProfileCommand(Command):
    actor: Principal
    changes: dict[str, object]  # only the fields the client sent, already validated by ProfileUpdateRequest


class UpdateProfileHandler(CommandHandler[UpdateProfileCommand, UserOut]):
    """FR-AUTH-007: the caller edits their own display_name, avatar_url and bio. Email is never changed here."""

    def __init__(self, repository: AuthRepository) -> None:
        self._repository = repository

    async def handle(self, command: UpdateProfileCommand) -> UserOut:
        user = await self._repository.update_profile(command.actor.user_id, command.changes)
        if user is None:
            raise UnauthorizedError("Account no longer available")
        logger.info(
            "profile updated",
            extra={"user_id": str(command.actor.user_id), "at": datetime.now(UTC).isoformat()},
        )
        return UserOut.model_validate(user)
