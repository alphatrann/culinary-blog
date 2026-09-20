from culinary_blog.auth.models import RefreshToken, User
from culinary_blog.auth.schemas import AuthSession, UserOut
from culinary_blog.auth.security import TokenService


class SessionIssuer:
    """Mints an access/refresh token pair. Persisting the refresh token is left to the caller's transaction."""

    def __init__(self, tokens: TokenService) -> None:
        self._tokens = tokens

    def issue(self, user: User, client_ip: str | None) -> tuple[AuthSession, RefreshToken]:
        refresh_token = self._tokens.generate_refresh_token()
        record = RefreshToken(
            user_id=user.id,
            token_hash=self._tokens.hash_refresh_token(refresh_token),
            expires_at=self._tokens.refresh_expiry(),
            created_by_ip=client_ip,
        )
        session = AuthSession(
            user=UserOut.model_validate(user),
            access_token=self._tokens.create_access_token(user.id, list(user.roles)),
            refresh_token=refresh_token,
        )
        return session, record
