"""SRS Appendix B: stable error codes are emitted as the `code` member of the problem+json response."""

import uuid
from datetime import timedelta

import jwt
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from culinary_blog.auth.security import TokenService
from culinary_blog.errors import (
    BadRequestError,
    ConflictError,
    ErrorCode,
    NotFoundError,
    UnauthorizedError,
)
from culinary_blog.problem_details import register_problem_handlers
from culinary_blog.recipes.schemas import IngredientIn
from culinary_blog.storage.images import MAX_IMAGE_BYTES, validate_image

SECRET = "test-secret-key-at-least-32-bytes-long"


class Payload(BaseModel):
    value: int


def make_client() -> TestClient:
    app = FastAPI()
    register_problem_handlers(app)

    @app.get("/coded")
    async def coded() -> None:
        raise NotFoundError("gone", code=ErrorCode.RECIPE_NOT_FOUND)

    @app.get("/plain")
    async def plain() -> None:
        raise ConflictError("clash")

    @app.post("/validate")
    async def validate(payload: Payload) -> None:
        return None

    @app.post("/ingredient")
    async def ingredient(payload: IngredientIn) -> None:
        return None

    return TestClient(app, raise_server_exceptions=False)


def test_domain_error_code_is_emitted():
    body = make_client().get("/coded").json()
    assert body["code"] == "RECIPE_NOT_FOUND" and body["status"] == 404


def test_domain_error_without_code_omits_member():
    assert "code" not in make_client().get("/plain").json()


def test_request_validation_error_has_validation_error_code():
    response = make_client().post("/validate", json={"value": "x"})
    assert response.status_code == 422 and response.json()["code"] == "VALIDATION_ERROR"


def test_quantity_without_unit_has_specific_code():
    response = make_client().post("/ingredient", json={"name": "Muối", "quantity": 1})
    assert response.status_code == 422 and response.json()["code"] == "INGREDIENT_QUANTITY_UNIT_MISMATCH"


def test_expired_access_token_code():
    tokens = TokenService(SECRET, timedelta(seconds=-5), timedelta(days=7))
    token = tokens.create_access_token(uuid.uuid4(), ["author"])
    with pytest.raises(UnauthorizedError) as exc:
        tokens.decode_access_token(token)
    assert exc.value.code == ErrorCode.AUTH_TOKEN_EXPIRED


def test_malformed_access_token_code():
    tokens = TokenService(SECRET, timedelta(minutes=15), timedelta(days=7))
    forged = jwt.encode({"sub": str(uuid.uuid4()), "exp": 9999999999}, "another-secret-key-32-bytes-long!!", "HS256")
    with pytest.raises(UnauthorizedError) as exc:
        tokens.decode_access_token(forged)
    assert exc.value.code == ErrorCode.AUTH_TOKEN_INVALID


@pytest.mark.parametrize(
    ("content_type", "data", "code"),
    [
        pytest.param("image/gif", b"GIF89a", ErrorCode.FILE_MIME_INVALID, id="mime"),
        pytest.param("image/png", b"\xff\xd8\xff" + b"0" * 10, ErrorCode.FILE_MIME_INVALID, id="magic"),
        pytest.param("image/jpeg", b"\xff\xd8\xff" + b"0" * MAX_IMAGE_BYTES, ErrorCode.FILE_SIZE_EXCEEDED, id="size"),
    ],
)
def test_image_validation_codes(content_type, data, code):
    with pytest.raises(BadRequestError) as exc:
        validate_image(content_type, data)
    assert exc.value.code == code
