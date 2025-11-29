"""
Middleware for request tracing and structured logging.

Phase 3.2: Production Hardening - Request Tracing
Adds correlation IDs and request context to all HTTP requests.
"""

from __future__ import annotations

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger, set_request_context, clear_request_context

logger = get_logger(__name__)


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add request tracing with correlation IDs.

    Features:
    - Generates or extracts X-Request-ID from headers
    - Sets request context for structured logging
    - Logs request start and completion with duration
    - Adds X-Request-ID to response headers
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Extract user ID from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)

        # Set request context for structured logging
        set_request_context(
            request_id=request_id,
            user_id=user_id if user_id else None,
        )

        # Log request start
        start_time = time.perf_counter()
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
        )

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log request completion
            logger.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log request failure
            logger.error(
                "request_failed",
                method=request.method,
                path=request.url.path,
                duration_ms=round(duration_ms, 2),
                error=str(e),
                error_type=type(e).__name__,
            )

            raise

        finally:
            # Clear request context to avoid leakage
            clear_request_context()
