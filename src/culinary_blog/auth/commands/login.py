import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from culinary_blog.auth.models import User
from culinary_blog.auth.repository import AuthRepository
from culinary_blog.auth.schemas import AuthSession
from culinary_blog.auth.security import PasswordHasher
from culinary_blog.auth.session_issuer import SessionIssuer
from culinary_blog.cqrs import Command, CommandHandler
from culinary_blog.errors import LockedError, UnauthorizedError

logger = logging.getLogger(__name__)

INVALID_CREDENTIALS = "Email hoặc mật khẩu không đúng"


@dataclass(frozen=True)
class LoginCommand(Command):
    email: str
    password: str
    client_ip: str | None = None


class LoginHandler(CommandHandler[LoginCommand, AuthSession]):
    """FR-AUTH-002: email/password login with lockout after repeated failures."""

    def __init__(
        self,
        repository: AuthRepository,
        hasher: PasswordHasher,
        issuer: SessionIssuer,
        max_failed_logins: int,
        lockout: timedelta,
    ) -> None:
        self._repository = repository
        self._hasher = hasher
        self._issuer = issuer
        self._max_failed_logins = max_failed_logins
        self._lockout = lockout

    async def handle(self, command: LoginCommand) -> AuthSession:
        user = await self._repository.get_user_by_email(command.email.lower())
        now = datetime.now(UTC)

        # Checked before the password so a locked account can't be used as a password oracle.
        if user is not None and user.locked_until is not None and user.locked_until > now:
            raise LockedError("Account is temporarily locked. Try again later.")

        # Always verifies (against a dummy hash when there is no user) to keep timing uniform.
        password_ok = await self._hasher.verify(command.password, user.password_hash if user else None)
        if user is None or not password_ok or not user.is_active:
            if user is not None and not password_ok:
                await self._record_failure(user, now)
            raise UnauthorizedError(INVALID_CREDENTIALS)

        user.failed_login_count = 0
        user.locked_until = None
        await self._repository.save_login_state(user)

        session, refresh_record = self._issuer.issue(user, command.client_ip)
        await self._repository.add_refresh_token(refresh_record)
        logger.info("user logged in", extra={"user_id": str(user.id), "at": now.isoformat()})
        return session

    async def _record_failure(self, user: User, now: datetime) -> None:
        user.failed_login_count += 1
        if user.failed_login_count >= self._max_failed_logins:
            user.locked_until = now + self._lockout
            user.failed_login_count = 0
            logger.warning("account locked after repeated failed logins", extra={"user_id": str(user.id)})
        await self._repository.save_login_state(user)
