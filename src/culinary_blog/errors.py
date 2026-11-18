from enum import StrEnum


class ErrorCode(StrEnum):
    """Stable machine-readable error codes (SRS Appendix B), emitted as the `code` member of the problem response."""

    AUTH_EMAIL_EXISTS = "AUTH_EMAIL_EXISTS"
    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    AUTH_TOKEN_INVALID = "AUTH_TOKEN_INVALID"
    AUTH_REFRESH_TOKEN_EXPIRED = "AUTH_REFRESH_TOKEN_EXPIRED"
    AUTH_REFRESH_TOKEN_REVOKED = "AUTH_REFRESH_TOKEN_REVOKED"
    AUTH_GOOGLE_TOKEN_INVALID = "AUTH_GOOGLE_TOKEN_INVALID"
    AUTH_ACCOUNT_LOCKED = "AUTH_ACCOUNT_LOCKED"
    RECIPE_NOT_FOUND = "RECIPE_NOT_FOUND"
    RECIPE_PUBLISH_INCOMPLETE = "RECIPE_PUBLISH_INCOMPLETE"
    RECIPE_FORBIDDEN = "RECIPE_FORBIDDEN"
    RECIPE_CONCURRENCY_CONFLICT = "RECIPE_CONCURRENCY_CONFLICT"
    INGREDIENT_QUANTITY_UNIT_MISMATCH = "INGREDIENT_QUANTITY_UNIT_MISMATCH"
    CATEGORY_NOT_FOUND = "CATEGORY_NOT_FOUND"
    CATEGORY_NAME_EXISTS = "CATEGORY_NAME_EXISTS"
    CATEGORY_DELETE_HAS_RECIPES = "CATEGORY_DELETE_HAS_RECIPES"
    FILE_SIZE_EXCEEDED = "FILE_SIZE_EXCEEDED"
    FILE_MIME_INVALID = "FILE_MIME_INVALID"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"


class DomainError(Exception):
    """Base for expected failures raised by handlers/repositories; the HTTP layer maps them to RFC 7807 responses."""

    status_code = 500
    title = "Internal Server Error"
    code: ErrorCode | None = None  # class-level default; an instance can override it via the `code` argument

    def __init__(
        self, detail: str | None = None, headers: dict[str, str] | None = None, code: ErrorCode | None = None
    ) -> None:
        super().__init__(detail or self.title)
        self.detail = detail or self.title
        self.headers = headers or {}
        if code is not None:
            self.code = code


class BadRequestError(DomainError):
    status_code = 400
    title = "Bad Request"


class UnauthorizedError(DomainError):
    status_code = 401
    title = "Unauthorized"


class ForbiddenError(DomainError):
    status_code = 403
    title = "Forbidden"


class NotFoundError(DomainError):
    status_code = 404
    title = "Not Found"


class ConflictError(DomainError):
    status_code = 409
    title = "Conflict"


class UnprocessableError(DomainError):
    """A well-formed request that references something invalid (e.g. a category that doesn't exist)."""

    status_code = 422
    title = "Unprocessable Entity"


class LockedError(DomainError):
    status_code = 423
    title = "Locked"


class ServiceUnavailableError(DomainError):
    """A required backing service (e.g. object storage) is unreachable."""

    status_code = 503
    title = "Service Unavailable"


class RateLimitedError(DomainError):
    status_code = 429
    title = "Too Many Requests"
    code = ErrorCode.RATE_LIMIT_EXCEEDED
