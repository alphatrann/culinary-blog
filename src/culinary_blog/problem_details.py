import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from culinary_blog.errors import DomainError

logger = logging.getLogger(__name__)

PROBLEM_JSON = "application/problem+json"


def _problem(request: Request, status: int, title: str, detail: str, **extra: object) -> JSONResponse:
    body = {"type": "about:blank", "title": title, "status": status, "detail": detail, "instance": request.url.path}
    return JSONResponse({**body, **extra}, status_code=status, media_type=PROBLEM_JSON)


async def _domain_error(request: Request, exc: DomainError) -> JSONResponse:
    return _problem(request, exc.status_code, exc.title, exc.detail)


async def _validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in exc.errors()]
    return _problem(request, 422, "Unprocessable Entity", "Request validation failed", errors=errors)


async def _http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return _problem(request, exc.status_code, str(exc.detail), str(exc.detail))


async def _unhandled_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled error", extra={"request_path": request.url.path})
    return _problem(request, 500, "Internal Server Error", "An unexpected error occurred")


def register_problem_handlers(app: FastAPI) -> None:
    """RFC 7807 `application/problem+json` for every error response (CONS-005)."""
    app.add_exception_handler(DomainError, _domain_error)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, _validation_error)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, _http_error)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, _unhandled_error)
