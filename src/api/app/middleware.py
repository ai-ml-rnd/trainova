"""Middleware for logging and request tracking."""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add request ID to each request."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log request/response details."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        status_code = response.status_code
        method = request.method
        url = request.url.path

        # Log in production
        if settings.is_production:
            import logging

            logging.info(
                f"{method} {url} {status_code} {process_time:.3f}s "
                f"request_id={request.headers.get('X-Request-ID')}"
            )

        return response


class TimeoutMiddleware(BaseHTTPMiddleware):
    """Add timeout to requests."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        import asyncio

        try:
            # Set a timeout for the request
            response = await asyncio.wait_for(
                call_next(request), timeout=settings.litellm_timeout
            )
            return response
        except asyncio.TimeoutError:
            return JSONResponse(
                status_code=504,
                content={
                    "error": "Gateway Timeout",
                    "message": "The request took too long to complete",
                },
            )


# Middleware stack
middleware_stack = [
    RequestIDMiddleware,
    RequestLoggingMiddleware,
    TimeoutMiddleware,
]
