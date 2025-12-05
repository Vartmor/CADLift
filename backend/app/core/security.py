"""
Security middleware for CADLift.

Phase 3.4: Production Hardening - Security
Provides rate limiting and security headers.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.

    Headers added:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Strict-Transport-Security: max-age=31536000; includeSubDomains (HTTPS only)
    - Content-Security-Policy: default-src 'self'
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Add HSTS header for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Content Security Policy (allow needed CDNs for frontend bundle)
        response.headers[
            "Content-Security-Policy"
        ] = (
            "default-src 'self' data: blob:; "
            "img-src 'self' data: blob: https://fastapi.tiangolo.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://aistudiocdn.com https://cdn.jsdelivr.net; "
            "connect-src 'self'; "
            "frame-ancestors 'self'"
        )

        # Remove server header if present (use del instead of pop for MutableHeaders)
        if "Server" in response.headers:
            del response.headers["Server"]

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.

    Limits requests per IP address to prevent abuse.

    Note: For production with multiple workers, consider using Redis-based rate limiting.
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 10000,  # Very high for development with polling
        requests_per_hour: int = 500000,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour

        # Storage: {ip_address: [(timestamp, count), ...]}
        self._minute_buckets: dict[str, list[tuple[float, int]]] = defaultdict(list)
        self._hour_buckets: dict[str, list[tuple[float, int]]] = defaultdict(list)

    def _clean_old_entries(self, ip: str, now: float) -> None:
        """Remove entries older than the time windows."""
        # Clean minute buckets (keep last 60 seconds)
        minute_cutoff = now - 60
        self._minute_buckets[ip] = [
            (ts, count) for ts, count in self._minute_buckets[ip] if ts > minute_cutoff
        ]

        # Clean hour buckets (keep last 3600 seconds)
        hour_cutoff = now - 3600
        self._hour_buckets[ip] = [
            (ts, count) for ts, count in self._hour_buckets[ip] if ts > hour_cutoff
        ]

    def _get_request_count(self, buckets: list[tuple[float, int]]) -> int:
        """Calculate total requests in time window."""
        return sum(count for _, count in buckets)

    def _is_rate_limited(self, ip: str) -> tuple[bool, str | None]:
        """
        Check if IP is rate limited.

        Returns:
            tuple: (is_limited, reason)
        """
        now = time.time()

        # Clean old entries
        self._clean_old_entries(ip, now)

        # Check minute limit
        minute_count = self._get_request_count(self._minute_buckets[ip])
        if minute_count >= self.requests_per_minute:
            return True, f"Rate limit exceeded: {self.requests_per_minute} requests per minute"

        # Check hour limit
        hour_count = self._get_request_count(self._hour_buckets[ip])
        if hour_count >= self.requests_per_hour:
            return True, f"Rate limit exceeded: {self.requests_per_hour} requests per hour"

        return False, None

    def _record_request(self, ip: str) -> None:
        """Record a request from the IP."""
        now = time.time()

        # Add to minute bucket
        self._minute_buckets[ip].append((now, 1))

        # Add to hour bucket
        self._hour_buckets[ip].append((now, 1))

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Skip rate limiting for health check endpoint
        if request.url.path == "/health":
            return await call_next(request)

        # Check rate limit
        is_limited, reason = self._is_rate_limited(client_ip)

        if is_limited:
            logger.warning(
                "rate_limit_exceeded",
                client_ip=client_ip,
                path=request.url.path,
                reason=reason,
            )

            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": reason,
                    "retry_after": 5,  # Seconds
                },
                headers={
                    "Retry-After": "5",
                    "X-RateLimit-Limit-Minute": str(self.requests_per_minute),
                    "X-RateLimit-Limit-Hour": str(self.requests_per_hour),
                },
            )

        # Record request
        self._record_request(client_ip)

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        minute_count = self._get_request_count(self._minute_buckets[client_ip])
        hour_count = self._get_request_count(self._hour_buckets[client_ip])

        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            max(0, self.requests_per_minute - minute_count)
        )
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(
            max(0, self.requests_per_hour - hour_count)
        )

        return response


class FileSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce file upload size limits.

    Rejects requests with Content-Length exceeding the limit.
    """

    def __init__(self, app, max_size: int = 50 * 1024 * 1024):
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check Content-Length header
        content_length = request.headers.get("content-length")

        if content_length:
            try:
                size = int(content_length)

                if size > self.max_size:
                    max_mb = self.max_size / (1024 * 1024)
                    actual_mb = size / (1024 * 1024)

                    logger.warning(
                        "file_size_limit_exceeded",
                        content_length=size,
                        max_size=self.max_size,
                        path=request.url.path,
                    )

                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": "file_too_large",
                            "message": f"File size {actual_mb:.1f}MB exceeds maximum allowed size of {max_mb:.0f}MB",
                            "max_size_bytes": self.max_size,
                        },
                    )
            except ValueError:
                pass  # Invalid Content-Length, let request proceed

        response = await call_next(request)
        return response
