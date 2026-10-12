import uuid
from datetime import timedelta

from fakeredis import FakeAsyncRedis, FakeServer
from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.testclient import TestClient

from culinary_blog.auth.dependencies import Authenticator
from culinary_blog.auth.security import TokenService
from culinary_blog.problem_details import register_problem_handlers
from culinary_blog.ratelimit.dependencies import ClientIpResolver, RateLimitGuard
from culinary_blog.ratelimit.limiter import SlidingWindowLimiter, TokenBucketLimiter

TRUSTED = ["10.0.0.0/8", "127.0.0.0/8"]


def _request(peer: str, xff: str | None = None) -> Request:
    headers = [(b"x-forwarded-for", xff.encode())] if xff else []
    return Request({"type": "http", "client": (peer, 1234), "headers": headers})


class TestClientIpResolver:
    resolver = ClientIpResolver(TRUSTED)

    def test_untrusted_peer_ignores_forwarded_header(self) -> None:
        assert self.resolver.resolve(_request("8.8.8.8", "1.2.3.4")) == "8.8.8.8"

    def test_trusted_proxy_uses_forwarded_client(self) -> None:
        assert self.resolver.resolve(_request("10.0.0.5", "203.0.113.9")) == "203.0.113.9"

    def test_spoofed_left_hops_are_skipped(self) -> None:
        assert self.resolver.resolve(_request("10.0.0.5", "6.6.6.6, 203.0.113.9")) == "203.0.113.9"

    def test_trusted_peer_without_header_is_the_peer(self) -> None:
        assert self.resolver.resolve(_request("10.0.0.5")) == "10.0.0.5"


def _app(limit: int = 2, peer: str = "10.0.0.5") -> TestClient:
    redis = FakeAsyncRedis(server=FakeServer())
    guard = RateLimitGuard(ClientIpResolver(TRUSTED))
    router = APIRouter(dependencies=[Depends(guard.per_ip(SlidingWindowLimiter(redis, "t", limit, 60, 90)))])
    router.add_api_route("/ping", lambda: {"ok": True}, methods=["GET"])
    app = FastAPI()
    register_problem_handlers(app)
    app.include_router(router)
    return TestClient(app, client=(peer, 50000))


def test_within_limit_sets_rate_limit_headers() -> None:
    response = _app().get("/ping")
    assert response.status_code == 200
    assert response.headers["X-RateLimit-Limit"] == "2"
    assert response.headers["X-RateLimit-Remaining"] == "1"
    assert int(response.headers["X-RateLimit-Reset"]) > 0
    assert "Retry-After" not in response.headers


def test_exceeding_limit_returns_429_problem_json() -> None:
    client = _app()
    client.get("/ping")
    client.get("/ping")
    response = client.get("/ping")
    assert response.status_code == 429
    assert response.headers["content-type"].startswith("application/problem+json")
    assert int(response.headers["Retry-After"]) >= 1
    assert response.headers["X-RateLimit-Remaining"] == "0"
    body = response.json()
    assert body["status"] == 429 and body["code"] == "RATE_LIMIT_EXCEEDED" and body["instance"] == "/ping"


def test_limit_is_per_client_ip() -> None:
    client = _app(limit=1)
    assert client.get("/ping", headers={"X-Forwarded-For": "203.0.113.1"}).status_code == 200
    assert client.get("/ping", headers={"X-Forwarded-For": "203.0.113.1"}).status_code == 429
    assert client.get("/ping", headers={"X-Forwarded-For": "203.0.113.2"}).status_code == 200


def test_token_bucket_dependency_blocks_after_burst() -> None:
    redis = FakeAsyncRedis(server=FakeServer())
    guard = RateLimitGuard(ClientIpResolver(TRUSTED))
    router = APIRouter(dependencies=[Depends(guard.per_ip(TokenBucketLimiter(redis, "api", 3, 60, 90)))])
    router.add_api_route("/r", lambda: {}, methods=["GET"])
    app = FastAPI()
    register_problem_handlers(app)
    app.include_router(router)
    client = TestClient(app, client=("10.0.0.5", 50000))
    assert [client.get("/r").status_code for _ in range(4)] == [200, 200, 200, 429]


class TestUploadLimit:
    def _client(self) -> tuple[TestClient, TokenService]:
        tokens = TokenService(
            "test-secret-key-test-secret-key-12", access_ttl=timedelta(minutes=5), refresh_ttl=timedelta(days=1)
        )
        authenticator = Authenticator(tokens)
        guard = RateLimitGuard(ClientIpResolver(TRUSTED))
        redis = FakeAsyncRedis(server=FakeServer())
        dep = guard.per_ip_and_user(SlidingWindowLimiter(redis, "upload", 2, 60, 90), authenticator)
        router = APIRouter()
        router.add_api_route("/up", lambda: {}, methods=["POST"], dependencies=[Depends(dep)])
        app = FastAPI()
        register_problem_handlers(app)
        app.include_router(router)
        return TestClient(app, client=("10.0.0.5", 50000)), tokens

    def _cookie(self, tokens: TokenService, user_id: uuid.UUID) -> dict[str, str]:
        return {"access_token": tokens.create_access_token(user_id, ["author"])}

    def test_user_limit_applies_across_ips(self) -> None:
        client, tokens = self._client()
        cookies = self._cookie(tokens, uuid.uuid4())
        statuses = [
            client.post("/up", cookies=cookies, headers={"X-Forwarded-For": f"203.0.113.{i}"}).status_code
            for i in range(3)
        ]
        assert statuses == [200, 200, 429]

    def test_ip_limit_applies_across_users(self) -> None:
        client, tokens = self._client()
        statuses = [
            client.post(
                "/up", cookies=self._cookie(tokens, uuid.uuid4()), headers={"X-Forwarded-For": "203.0.113.7"}
            ).status_code
            for _ in range(3)
        ]
        assert statuses == [200, 200, 429]

    def test_unauthenticated_upload_is_401_not_rate_limited(self) -> None:
        client, _ = self._client()
        assert client.post("/up").status_code == 401


def test_method_filter_skips_writes() -> None:
    redis = FakeAsyncRedis(server=FakeServer())
    guard = RateLimitGuard(ClientIpResolver(TRUSTED))
    dep = guard.per_ip(TokenBucketLimiter(redis, "api", 1, 60, 90), methods=frozenset({"GET"}))
    router = APIRouter(dependencies=[Depends(dep)])
    router.add_api_route("/r", lambda: {}, methods=["GET", "POST"])
    app = FastAPI()
    register_problem_handlers(app)
    app.include_router(router)
    client = TestClient(app, client=("10.0.0.5", 50000))
    assert [client.post("/r").status_code for _ in range(3)] == [200, 200, 200]
    assert [client.get("/r").status_code for _ in range(2)] == [200, 429]
