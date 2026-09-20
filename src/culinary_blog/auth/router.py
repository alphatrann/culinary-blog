from fastapi import APIRouter, Request, Response

from culinary_blog.auth.commands.login import LoginCommand, LoginHandler
from culinary_blog.auth.commands.logout import LogoutCommand, LogoutHandler
from culinary_blog.auth.commands.refresh import RefreshCommand, RefreshHandler
from culinary_blog.auth.commands.register import RegisterCommand, RegisterHandler
from culinary_blog.auth.cookies import REFRESH_COOKIE, AuthCookies
from culinary_blog.auth.dependencies import Authenticator
from culinary_blog.auth.queries.get_current_user import GetCurrentUserHandler, GetCurrentUserQuery
from culinary_blog.auth.schemas import AuthSession, LoginRequest, RegisterRequest, UserOut
from culinary_blog.errors import UnauthorizedError


class AuthRouter:
    """HTTP adapter for auth: parses requests, sets/clears cookies, delegates to handlers."""

    def __init__(
        self,
        authenticator: Authenticator,
        cookies: AuthCookies,
        register: RegisterHandler,
        login: LoginHandler,
        refresh: RefreshHandler,
        logout: LogoutHandler,
        get_current_user: GetCurrentUserHandler,
    ) -> None:
        self._authenticator = authenticator
        self._cookies = cookies
        self._register = register
        self._login = login
        self._refresh = refresh
        self._logout = logout
        self._get_current_user = get_current_user

        self.router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
        self.router.add_api_route("/register", self.register, methods=["POST"], response_model=UserOut, status_code=201)
        self.router.add_api_route("/login", self.login, methods=["POST"], response_model=UserOut)
        self.router.add_api_route("/refresh", self.refresh, methods=["POST"], response_model=UserOut)
        self.router.add_api_route("/logout", self.logout, methods=["POST"], status_code=204)
        self.router.add_api_route("/me", self.me, methods=["GET"], response_model=UserOut)

    async def register(self, body: RegisterRequest, request: Request, response: Response) -> UserOut:
        session = await self._register.handle(
            RegisterCommand(body.display_name, str(body.email), body.password, self._client_ip(request))
        )
        return self._with_cookies(session, response)

    async def login(self, body: LoginRequest, request: Request, response: Response) -> UserOut:
        session = await self._login.handle(LoginCommand(str(body.email), body.password, self._client_ip(request)))
        return self._with_cookies(session, response)

    async def refresh(self, request: Request, response: Response) -> UserOut:
        token = request.cookies.get(REFRESH_COOKIE)
        if not token:
            raise UnauthorizedError("Missing refresh token")
        session = await self._refresh.handle(RefreshCommand(token, self._client_ip(request)))
        return self._with_cookies(session, response)

    async def logout(self, request: Request) -> Response:
        actor = await self._authenticator.require_principal(request)
        await self._logout.handle(LogoutCommand(actor, request.cookies.get(REFRESH_COOKIE)))
        response = Response(status_code=204)
        self._cookies.clear(response)
        return response

    async def me(self, request: Request) -> UserOut:
        actor = await self._authenticator.require_principal(request)
        return await self._get_current_user.handle(GetCurrentUserQuery(actor))

    def _with_cookies(self, session: AuthSession, response: Response) -> UserOut:
        self._cookies.set(response, session.access_token, session.refresh_token)
        return session.user

    @staticmethod
    def _client_ip(request: Request) -> str | None:
        return request.client.host if request.client else None
