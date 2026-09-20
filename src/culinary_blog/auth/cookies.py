from datetime import timedelta

from fastapi import Response

ACCESS_COOKIE = "access_token"
REFRESH_COOKIE = "refresh_token"

# The refresh cookie is scoped to the auth routes: sent to /refresh and /logout (which must revoke it), nowhere else.
REFRESH_COOKIE_PATH = "/api/v1/auth"


class AuthCookies:
    """Sets/clears the HttpOnly auth cookies (CONS-004). Tokens never appear in a response body."""

    def __init__(self, secure: bool, access_ttl: timedelta, refresh_ttl: timedelta) -> None:
        self._secure = secure
        self._access_max_age = int(access_ttl.total_seconds())
        self._refresh_max_age = int(refresh_ttl.total_seconds())

    def set(self, response: Response, access_token: str, refresh_token: str) -> None:
        response.set_cookie(
            ACCESS_COOKIE,
            access_token,
            max_age=self._access_max_age,
            path="/",
            httponly=True,
            secure=self._secure,
            samesite="lax",
        )
        response.set_cookie(
            REFRESH_COOKIE,
            refresh_token,
            max_age=self._refresh_max_age,
            path=REFRESH_COOKIE_PATH,
            httponly=True,
            secure=self._secure,
            samesite="lax",
        )

    def clear(self, response: Response) -> None:
        response.delete_cookie(ACCESS_COOKIE, path="/", httponly=True, secure=self._secure, samesite="lax")
        response.delete_cookie(
            REFRESH_COOKIE, path=REFRESH_COOKIE_PATH, httponly=True, secure=self._secure, samesite="lax"
        )
