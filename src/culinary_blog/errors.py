class DomainError(Exception):
    """Base for expected failures raised by handlers/repositories; the HTTP layer maps them to RFC 7807 responses."""

    status_code = 500
    title = "Internal Server Error"

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail or self.title)
        self.detail = detail or self.title


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
