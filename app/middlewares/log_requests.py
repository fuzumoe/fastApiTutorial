import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger

logger = get_logger(__name__)

CallNext = Callable[[Request], Awaitable[Response]]


async def log_requests(request: Request, call_next: CallNext) -> Response:
    start_time: float = time.time()

    logger.info(f"Request started: {request.method} {request.url.path}")

    try:
        response: Response = await call_next(request)

        process_time: float = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.6f}"

        logger.info(
            f"Request completed: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Duration: {process_time:.6f}s"
        )

        return response
    except Exception as exc:
        exception_time: float = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url.path} - "
            f"Duration: {exception_time:.6f}s - Error: {exc!s}"
        )
        raise


class LogRequestsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: CallNext) -> Response:
        start_time = time.time()

        response: Response = await call_next(request)

        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.6f}"

        return response
