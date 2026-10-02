from opentelemetry import trace

from culinary_blog.auth.models import RefreshToken, User
from culinary_blog.auth.schemas import AuthSession, UserOut
from culinary_blog.auth.security import TokenService

# See security.py's _tracer comment (M6a/ADR-0009): covers the gap between the
# login-state-save and add-refresh-token transactions in Tempo traces.
_tracer = trace.get_tracer(__name__)


class SessionIssuer:
    """Mints an access/refresh token pair. Persisting the refresh token is left to the caller's transaction."""

    def __init__(self, tokens: TokenService) -> None:
        self._tokens = tokens

    def issue(self, user: User, client_ip: str | None) -> tuple[AuthSession, RefreshToken]:
        with _tracer.start_as_current_span("session_issuer.issue"):
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
