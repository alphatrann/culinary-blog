import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from culinary_blog.auth.google import GoogleIdTokenVerifier
from culinary_blog.auth.models import User
from culinary_blog.auth.repository import AuthRepository
from culinary_blog.auth.schemas import AuthSession
from culinary_blog.auth.session_issuer import SessionIssuer
from culinary_blog.cqrs import Command, CommandHandler
from culinary_blog.errors import BadRequestError, LockedError, UnauthorizedError

logger = logging.getLogger(__name__)

AVATAR_MAX_LENGTH = 500  # User.avatar_url column length


@dataclass(frozen=True)
class GoogleLoginCommand(Command):
    id_token: str
    client_ip: str | None = None


class GoogleLoginHandler(CommandHandler[GoogleLoginCommand, AuthSession]):
    """FR-AUTH-003: signs in (or registers) with a verified Google ID token.

    Lookup order: google_sub, then email. An email match is linked to the Google subject only when Google
    confirms the address, so an unverified claim can't take over a password account.
    """

    def __init__(self, repository: AuthRepository, verifier: GoogleIdTokenVerifier, issuer: SessionIssuer) -> None:
        self._repository = repository
        self._verifier = verifier
        self._issuer = issuer

    async def handle(self, command: GoogleLoginCommand) -> AuthSession:
        profile = await self._verifier.verify(command.id_token)
        if not profile.email:
            raise BadRequestError("Google account has no email address")
        if not profile.email_verified:
            raise UnauthorizedError("Google email address is not verified")

        email = profile.email.lower()
        now = datetime.now(UTC)
        user = await self._repository.get_user_by_google_sub(profile.sub)
        created = user is None
        if user is None:
            user = await self._repository.get_user_by_email(email)
            created = user is None
            if created:
                user = User(
                    email=email,
                    display_name=(profile.name or email.split("@")[0])[:100],
                    avatar_url=profile.picture
                    if profile.picture and len(profile.picture) <= AVATAR_MAX_LENGTH
                    else None,
                    roles=["author"],
                    google_sub=profile.sub,
                    email_confirmed=True,
                )
            else:
                user.google_sub = profile.sub
                await self._repository.save_login_state(user)

        if not user.is_active:
            raise UnauthorizedError("Account is inactive")
        if user.locked_until is not None and user.locked_until > now:
            raise LockedError("Account is temporarily locked. Try again later.")

        session, refresh_record = self._issuer.issue(user, command.client_ip)
        if created:
            # shortcut: racing first sign-ins for one account 409 instead of retrying, retry once if seen in logs
            await self._repository.create_user_with_refresh_token(user, refresh_record)
            logger.info("user registered", extra={"user_id": str(user.id), "at": now.isoformat()})
        else:
            await self._repository.add_refresh_token(refresh_record)
            logger.info("user logged in", extra={"user_id": str(user.id), "at": now.isoformat()})
        return session
