from datetime import timedelta
from functools import lru_cache

from fastapi import APIRouter

from culinary_blog.auth.commands.google_login import GoogleLoginHandler
from culinary_blog.auth.commands.login import LoginHandler
from culinary_blog.auth.commands.logout import LogoutHandler
from culinary_blog.auth.commands.refresh import RefreshHandler
from culinary_blog.auth.commands.register import RegisterHandler
from culinary_blog.auth.commands.update_profile import UpdateProfileHandler
from culinary_blog.auth.cookies import AuthCookies
from culinary_blog.auth.dependencies import Authenticator
from culinary_blog.auth.google import GoogleIdTokenVerifier
from culinary_blog.auth.queries.get_current_user import GetCurrentUserHandler
from culinary_blog.auth.repository import AuthRepository
from culinary_blog.auth.router import AuthRouter
from culinary_blog.auth.security import PasswordHasher, TokenService
from culinary_blog.auth.session_issuer import SessionIssuer
from culinary_blog.cache.redis import get_queue_redis
from culinary_blog.config import get_settings
from culinary_blog.database.session import async_session_factory, read_session_factory
from culinary_blog.jobs.queue import RedisJobQueue


@lru_cache
def get_token_service() -> TokenService:
    settings = get_settings()
    return TokenService(
        settings.jwt_secret_key,
        access_ttl=timedelta(minutes=settings.access_token_ttl_minutes),
        refresh_ttl=timedelta(days=settings.refresh_token_ttl_days),
    )


@lru_cache
def get_authenticator() -> Authenticator:
    """Shared with other modules' routers so every protected endpoint authenticates identically."""
    return Authenticator(get_token_service())


def build_auth_router() -> APIRouter:
    """Composition root for the auth module: the only place that binds concrete dependencies."""
    settings = get_settings()
    tokens = get_token_service()
    repository = AuthRepository(async_session_factory, read_session_factory)
    hasher = PasswordHasher()
    issuer = SessionIssuer(tokens)
    return AuthRouter(
        authenticator=get_authenticator(),
        cookies=AuthCookies(settings.cookie_secure, tokens.access_ttl, tokens.refresh_ttl),
        register=RegisterHandler(repository, hasher, issuer, RedisJobQueue(get_queue_redis())),
        login=LoginHandler(
            repository,
            hasher,
            issuer,
            max_failed_logins=settings.max_failed_logins,
            lockout=timedelta(minutes=settings.lockout_minutes),
        ),
        refresh=RefreshHandler(repository, tokens, issuer),
        logout=LogoutHandler(repository, tokens),
        get_current_user=GetCurrentUserHandler(repository),
        google_login=GoogleLoginHandler(repository, GoogleIdTokenVerifier(settings.google_client_id), issuer),
        update_profile=UpdateProfileHandler(repository),
    ).router
