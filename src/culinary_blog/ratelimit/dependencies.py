"""FastAPI dependencies enforcing the rate limits (HTTP layer; the algorithms live in `limiter.py`)."""

import ipaddress
import time
from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, Request, Response

from culinary_blog.auth.dependencies import Authenticator
from culinary_blog.auth.principal import Principal
from culinary_blog.errors import RateLimitedError
from culinary_blog.ratelimit.limiter import Limiter, RateLimitResult


class ClientIpResolver:
    """Real client IP behind nginx: walk X-Forwarded-For from the right, skipping trusted proxies (not spoofable)."""

    def __init__(self, trusted_proxies: list[str]) -> None:
        self._networks = [ipaddress.ip_network(item, strict=False) for item in trusted_proxies]

    def _trusted(self, host: str) -> bool:
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            return False
        return any(address in network for network in self._networks)

    def resolve(self, request: Request) -> str:
        peer = request.client.host if request.client else "unknown"
        if not self._trusted(peer):
            return peer
        hops = [h.strip() for h in request.headers.get("x-forwarded-for", "").split(",") if h.strip()]
        for hop in reversed(hops):
            if not self._trusted(hop):
                return hop
        return hops[0] if hops else peer


class RateLimitGuard:
    """Builds the per-class dependencies. Each denied request gets a 429 problem+json with Retry-After."""

    def __init__(self, ip_resolver: ClientIpResolver) -> None:
        self._ip = ip_resolver

    @staticmethod
    def _headers(result: RateLimitResult) -> dict[str, str]:
        return {
            "X-RateLimit-Limit": str(result.limit),
            "X-RateLimit-Remaining": str(result.remaining),
            "X-RateLimit-Reset": str(int(time.time()) + result.reset_in),
        }

    def _enforce(self, result: RateLimitResult, response: Response) -> None:
        headers = self._headers(result)
        if not result.allowed:
            headers["Retry-After"] = str(result.retry_after)
            raise RateLimitedError("Rate limit exceeded. Retry later.", headers=headers)
        response.headers.update(headers)

    def per_ip(
        self, limiter: Limiter, methods: frozenset[str] | None = None
    ) -> Callable[[Request, Response], Awaitable[None]]:
        """Limit by client IP; with `methods`, requests using any other method are not counted."""

        async def dependency(request: Request, response: Response) -> None:
            if methods is not None and request.method not in methods:
                return
            self._enforce(await limiter.check(self._ip.resolve(request)), response)

        return dependency

    def per_ip_and_user(self, limiter: Limiter, authenticator: Authenticator) -> Callable[..., Awaitable[None]]:
        """Both the IP and the authenticated user must be within limits (upload, NFR-SEC-003)."""

        async def dependency(
            request: Request,
            response: Response,
            principal: Annotated[Principal, Depends(authenticator.require_principal)],
        ) -> None:
            ip_result = await limiter.check(f"ip:{self._ip.resolve(request)}")
            if not ip_result.allowed:
                self._enforce(ip_result, response)
            self._enforce(await limiter.check(f"user:{principal.user_id}"), response)

        return dependency
