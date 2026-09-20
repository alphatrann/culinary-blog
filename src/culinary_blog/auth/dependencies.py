from fastapi import Request

from culinary_blog.auth.cookies import ACCESS_COOKIE
from culinary_blog.auth.principal import Principal
from culinary_blog.auth.security import TokenService
from culinary_blog.errors import UnauthorizedError


class Authenticator:
    """FastAPI dependencies that turn the `access_token` cookie into a Principal.

    Only authenticates. Role checks live in the command handlers so they can't be bypassed by another entry point.
    """

    def __init__(self, tokens: TokenService) -> None:
        self._tokens = tokens

    async def require_principal(self, request: Request) -> Principal:
        token = request.cookies.get(ACCESS_COOKIE)
        if not token:
            raise UnauthorizedError("Not authenticated")
        return self._tokens.decode_access_token(token)

    async def optional_principal(self, request: Request) -> Principal | None:
        """For public endpoints that show more to a logged-in caller; a bad/expired cookie just means guest."""
        token = request.cookies.get(ACCESS_COOKIE)
        if not token:
            return None
        try:
            return self._tokens.decode_access_token(token)
        except UnauthorizedError:
            return None
