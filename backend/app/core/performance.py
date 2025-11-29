"""
Performance monitoring utilities for CADLift.

Phase 3.3: Production Hardening - Performance Monitoring
Provides operation timing, profiling, and performance metrics.
"""

from __future__ import annotations

import cProfile
import functools
import pstats
import time
from io import StringIO
from typing import Any, Callable, TypeVar

from app.core.logging import get_logger

logger = get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def timed_operation(operation_name: str | None = None) -> Callable[[F], F]:
    """
    Decorator to log operation duration with structured logging.

    Args:
        operation_name: Name of the operation (defaults to function name)

    Returns:
        Decorated function that logs timing information

    Example:
        @timed_operation("dxf_parsing")
        def parse_dxf_file(path):
            ...

        # Logs: {"event": "operation_completed", "operation": "dxf_parsing", "duration_ms": 123.45}
    """

    def decorator(func: F) -> F:
        op_name = operation_name or func.__name__

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()

            try:
                result = func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start) * 1000

                logger.info(
                    "operation_completed",
                    operation=op_name,
                    duration_ms=round(duration_ms, 2),
                    success=True,
                )

                return result
            except Exception as e:
                duration_ms = (time.perf_counter() - start) * 1000
                logger.error(
                    "operation_failed",
                    operation=op_name,
                    duration_ms=round(duration_ms, 2),
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()

            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start) * 1000

                logger.info(
                    "operation_completed",
                    operation=op_name,
                    duration_ms=round(duration_ms, 2),
                    success=True,
                )

                return result
            except Exception as e:
                duration_ms = (time.perf_counter() - start) * 1000
                logger.error(
                    "operation_failed",
                    operation=op_name,
                    duration_ms=round(duration_ms, 2),
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise

        # Return async wrapper if function is coroutine, otherwise sync wrapper
        if functools.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper  # type: ignore

    return decorator


def profile_if_slow(threshold_seconds: float = 5.0) -> Callable[[F], F]:
    """
    Decorator to profile function if it takes longer than threshold.

    Args:
        threshold_seconds: Minimum duration to trigger profiling (default: 5s)

    Returns:
        Decorated function that profiles slow executions

    Example:
        @profile_if_slow(threshold_seconds=3.0)
        def slow_operation():
            ...

        # If operation takes >3s, logs profiling stats
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            profiler = cProfile.Profile()
            start = time.perf_counter()

            profiler.enable()
            try:
                result = func(*args, **kwargs)
            finally:
                profiler.disable()

            duration = time.perf_counter() - start

            if duration > threshold_seconds:
                # Generate profile stats
                s = StringIO()
                ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
                ps.print_stats(20)  # Top 20 slowest functions

                logger.warning(
                    "slow_operation_profiled",
                    function=func.__name__,
                    duration_s=round(duration, 2),
                    threshold_s=threshold_seconds,
                    profile_stats=s.getvalue(),
                )

            return result

        return wrapper  # type: ignore

    return decorator


class PerformanceTimer:
    """
    Context manager for timing code blocks.

    Example:
        with PerformanceTimer("database_query") as timer:
            results = await db.execute(query)

        # Automatically logs timing information
    """

    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time: float = 0
        self.duration_ms: float = 0

    def __enter__(self) -> PerformanceTimer:
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.duration_ms = (time.perf_counter() - self.start_time) * 1000

        if exc_type is None:
            logger.info(
                "timer_completed",
                operation=self.operation_name,
                duration_ms=round(self.duration_ms, 2),
            )
        else:
            logger.error(
                "timer_failed",
                operation=self.operation_name,
                duration_ms=round(self.duration_ms, 2),
                error=str(exc_val),
                error_type=exc_type.__name__ if exc_type else None,
            )


class PerformanceMetrics:
    """
    Simple in-memory performance metrics tracker.

    Tracks operation counts, durations, and errors for monitoring.

    Example:
        metrics = PerformanceMetrics()
        metrics.record_operation("dxf_parse", duration_ms=123.45, success=True)
        stats = metrics.get_stats()  # Get summary statistics
    """

    def __init__(self) -> None:
        self._operations: dict[str, list[float]] = {}
        self._errors: dict[str, int] = {}
        self._counts: dict[str, int] = {}

    def record_operation(
        self, operation_name: str, duration_ms: float, success: bool = True
    ) -> None:
        """Record an operation execution."""
        if operation_name not in self._operations:
            self._operations[operation_name] = []
            self._errors[operation_name] = 0
            self._counts[operation_name] = 0

        self._operations[operation_name].append(duration_ms)
        self._counts[operation_name] += 1

        if not success:
            self._errors[operation_name] += 1

    def get_stats(self, operation_name: str | None = None) -> dict[str, Any]:
        """
        Get performance statistics.

        Args:
            operation_name: Specific operation to get stats for (None = all operations)

        Returns:
            Dictionary with performance metrics
        """
        if operation_name:
            if operation_name not in self._operations:
                return {}

            durations = self._operations[operation_name]
            return {
                "operation": operation_name,
                "count": self._counts[operation_name],
                "errors": self._errors[operation_name],
                "error_rate": self._errors[operation_name] / self._counts[operation_name]
                if self._counts[operation_name] > 0
                else 0,
                "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
                "min_duration_ms": min(durations) if durations else 0,
                "max_duration_ms": max(durations) if durations else 0,
                "total_duration_ms": sum(durations),
            }

        # Return stats for all operations
        return {
            op: self.get_stats(op) for op in self._operations.keys()
        }

    def reset(self) -> None:
        """Clear all metrics."""
        self._operations.clear()
        self._errors.clear()
        self._counts.clear()


# Global metrics instance
global_metrics = PerformanceMetrics()
