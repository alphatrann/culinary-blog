from datetime import timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from culinary_blog.auth.commands.login import LoginHandler
from culinary_blog.auth.commands.logout import LogoutHandler
from culinary_blog.auth.commands.refresh import RefreshHandler
from culinary_blog.auth.commands.register import RegisterHandler
from culinary_blog.auth.cookies import AuthCookies
from culinary_blog.auth.dependencies import Authenticator
from culinary_blog.auth.queries.get_current_user import GetCurrentUserHandler
from culinary_blog.auth.router import AuthRouter
from culinary_blog.problem_details import register_problem_handlers
from tests.auth.fakes import PASSWORD, Services, make_services

REGISTER = {"display_name": "Cook", "email": "cook@example.com", "password": PASSWORD}
LOGIN = {"email": "cook@example.com", "password": PASSWORD}


def make_client() -> tuple[TestClient, Services]:
    s = make_services()
    router = AuthRouter(
        authenticator=Authenticator(s.tokens),
        cookies=AuthCookies(False, s.tokens.access_ttl, s.tokens.refresh_ttl),  # http://testserver, so not Secure
        register=RegisterHandler(s.repository, s.hasher, s.issuer),
        login=LoginHandler(s.repository, s.hasher, s.issuer, 5, timedelta(minutes=15)),
        refresh=RefreshHandler(s.repository, s.tokens, s.issuer),
        logout=LogoutHandler(s.repository, s.tokens),
        get_current_user=GetCurrentUserHandler(s.repository),
    ).router
    app = FastAPI()
    register_problem_handlers(app)
    app.include_router(router)
    return TestClient(app), s


@pytest.fixture
def client() -> TestClient:
    return make_client()[0]


def set_cookie_headers(response) -> list[str]:
    return response.headers.get_list("set-cookie")


# --- register -------------------------------------------------------------------------------------------------------


def test_register_returns_user_and_sets_httponly_cookies_without_tokens_in_body(client):
    response = client.post("/api/v1/auth/register", json=REGISTER)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "cook@example.com" and body["roles"] == ["author"]
    assert not {"access_token", "refresh_token", "password_hash"} & body.keys()

    cookies = {h.split("=", 1)[0]: h.lower() for h in set_cookie_headers(response)}
    assert set(cookies) == {"access_token", "refresh_token"}
    assert all("httponly" in h and "samesite=lax" in h for h in cookies.values())
    assert "path=/api/v1/auth" in cookies["refresh_token"]


def test_register_duplicate_email_is_409_problem_json(client):
    client.post("/api/v1/auth/register", json=REGISTER)
    response = client.post("/api/v1/auth/register", json=REGISTER)

    assert response.status_code == 409
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["status"] == 409


@pytest.mark.parametrize(
    "override",
    [
        {"password": "alllowercase1!"},  # no uppercase
        {"password": "NoDigits!!"},
        {"password": "NoSpecial123"},
        {"password": "Sh0rt!"},
        {"email": "not-an-email"},
        {"display_name": "x"},
    ],
)
def test_register_invalid_input_is_422(client, override):
    response = client.post("/api/v1/auth/register", json={**REGISTER, **override})
    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")


# --- login ----------------------------------------------------------------------------------------------------------


def test_login_success_sets_cookies(client):
    client.post("/api/v1/auth/register", json=REGISTER)
    client.cookies.clear()

    response = client.post("/api/v1/auth/login", json=LOGIN)
    assert response.status_code == 200
    assert "access_token" in client.cookies and "refresh_token" in client.cookies


def test_login_wrong_password_is_401_and_sets_no_cookies(client):
    client.post("/api/v1/auth/register", json=REGISTER)
    client.cookies.clear()

    response = client.post("/api/v1/auth/login", json={**LOGIN, "password": "Wrong!Pass1"})
    assert response.status_code == 401
    assert not set_cookie_headers(response)


def test_login_locks_account_after_five_failures_with_423(client):
    client.post("/api/v1/auth/register", json=REGISTER)
    for _ in range(5):
        client.post("/api/v1/auth/login", json={**LOGIN, "password": "Wrong!Pass1"})

    assert client.post("/api/v1/auth/login", json=LOGIN).status_code == 423


# --- protected endpoint ---------------------------------------------------------------------------------------------


def test_me_with_cookie_returns_current_user(client):
    client.post("/api/v1/auth/register", json=REGISTER)
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == "cook@example.com"


def test_me_without_or_with_garbage_cookie_is_401(client):
    assert client.get("/api/v1/auth/me").status_code == 401
    client.cookies.set("access_token", "garbage")
    assert client.get("/api/v1/auth/me").status_code == 401


# --- refresh --------------------------------------------------------------------------------------------------------


def test_refresh_rotates_cookie_and_old_token_is_rejected_on_reuse(client):
    client.post("/api/v1/auth/register", json=REGISTER)
    old_refresh = client.cookies["refresh_token"]

    assert client.post("/api/v1/auth/refresh").status_code == 200
    assert client.cookies["refresh_token"] != old_refresh

    client.cookies.set("refresh_token", old_refresh, path="/api/v1/auth")
    assert client.post("/api/v1/auth/refresh").status_code == 401


def test_refresh_without_cookie_is_401(client):
    assert client.post("/api/v1/auth/refresh").status_code == 401


# --- logout ---------------------------------------------------------------------------------------------------------


def test_logout_revokes_refresh_token_and_clears_cookies(client):
    client.post("/api/v1/auth/register", json=REGISTER)
    refresh = client.cookies["refresh_token"]

    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 204
    assert all("max-age=0" in h.lower() for h in set_cookie_headers(response))
    assert "access_token" not in client.cookies

    client.cookies.set("refresh_token", refresh, path="/api/v1/auth")
    assert client.post("/api/v1/auth/refresh").status_code == 401  # revoked token rejected


def test_logout_requires_authentication(client):
    assert client.post("/api/v1/auth/logout").status_code == 401
