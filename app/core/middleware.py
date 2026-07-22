import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response

request_logger = logging.getLogger("request_logger")


async def request_logging_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    started_at = time.perf_counter()
    client_host = request.client.host if request.client else "unknown"

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        request_logger.exception(
            "Unhandled request error | method=%s path=%s client=%s duration_ms=%s",
            request.method,
            request.url.path,
            client_host,
            duration_ms,
        )
        raise

    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    request_logger.info(
        "Request completed | method=%s path=%s status=%s client=%s duration_ms=%s",
        request.method,
        request.url.path,
        response.status_code,
        client_host,
        duration_ms,
    )

    return response
