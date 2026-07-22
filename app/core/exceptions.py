from fastapi import status


class AppException(Exception):
    """Base application exception with HTTP status and error code."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "internal_error"
    message: str = "Internal server error"

    def __init__(
        self,
        message: str | None = None,
        *,
        status_code: int | None = None,
        error_code: str | None = None,
    ) -> None:
        self.message = message or self.message
        self.status_code = status_code or self.status_code
        self.error_code = error_code or self.error_code
        super().__init__(self.message)


class RateLimitExceededException(AppException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "rate_limit_exceeded"
    message = "Too many requests. Please try again later."


class StorageException(AppException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "storage_error"
    message = "Storage operation failed."
