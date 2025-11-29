"""
Structured logging configuration for CADLift.

Phase 3.2: Production Hardening - Structured Logging
Provides JSON-formatted logs with request tracing and context propagation.
"""

from __future__ import annotations

import logging
import sys
from contextvars import ContextVar
from typing import Any

import structlog

# Context variables for request tracing
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
user_id_var: ContextVar[str] = ContextVar("user_id", default="")
job_id_var: ContextVar[str] = ContextVar("job_id", default="")


def add_context_to_event(
    logger: logging.Logger, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """
    Add context variables (request_id, user_id, job_id) to every log event.
    """
    # Add request/user/job IDs if available
    request_id = request_id_var.get("")
    if request_id:
        event_dict["request_id"] = request_id

    user_id = user_id_var.get("")
    if user_id:
        event_dict["user_id"] = user_id

    job_id = job_id_var.get("")
    if job_id:
        event_dict["job_id"] = job_id

    return event_dict


def configure_logging(
    *,
    json_logs: bool = True,
    log_level: str = "INFO",
    include_stdlib: bool = True,
) -> None:
    """
    Configure structured logging with JSON output.

    Args:
        json_logs: If True, output JSON format. If False, use console format for development.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        include_stdlib: If True, configure standard library logging to use structlog
    """
    # Configure processors based on output format
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        add_context_to_event,  # Add request/user/job IDs
    ]

    if json_logs:
        # Production: JSON output
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Development: Console output with colors
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging to use structlog
    if include_stdlib:
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=getattr(logging, log_level.upper()),
        )

        # Redirect stdlib loggers to structlog
        logging.getLogger().handlers.clear()
        logging.getLogger().addHandler(
            logging.StreamHandler(sys.stdout)
        )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structlog logger

    Example:
        logger = get_logger(__name__)
        logger.info("job_started", job_id=job.id, pipeline=job.mode)
        logger.error("job_failed", job_id=job.id, error=str(e))
    """
    return structlog.get_logger(name)


def set_request_context(
    *,
    request_id: str | None = None,
    user_id: str | None = None,
    job_id: str | None = None,
) -> None:
    """
    Set context variables for the current request/job.

    This allows all log messages to automatically include these IDs
    without manually passing them to every log call.

    Args:
        request_id: HTTP request ID (X-Request-ID header)
        user_id: User ID for the current request
        job_id: Job ID being processed

    Example:
        set_request_context(request_id="abc123", user_id="user_1", job_id="job_42")
        logger.info("processing")  # Automatically includes all IDs
    """
    if request_id:
        request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)
    if job_id:
        job_id_var.set(job_id)


def clear_request_context() -> None:
    """
    Clear all context variables.

    Call this at the end of request processing to avoid context leakage.
    """
    request_id_var.set("")
    user_id_var.set("")
    job_id_var.set("")


# Configure logging on module import
# Can be overridden by calling configure_logging() explicitly
configure_logging(
    json_logs=True,  # Use JSON in production
    log_level="INFO",
)
