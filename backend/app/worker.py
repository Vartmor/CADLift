"""
Celery worker for background job processing.

NOTE: This module requires celery and redis which are optional dependencies.
When ENABLE_TASK_QUEUE=false, this module is not used.
"""
import asyncio
import time

# Celery is optional - only needed when ENABLE_TASK_QUEUE=true
try:
    from celery import Celery
    CELERY_AVAILABLE = True
except ImportError:
    Celery = None
    CELERY_AVAILABLE = False

from app.core.config import get_settings
from app.core.errors import CADLiftError
from app.core.logging import configure_logging, get_logger, set_request_context, clear_request_context
from app.core.performance import timed_operation
from app.db.session import AsyncSessionLocal
from app.models import Job
from app.pipelines import cad, image, prompt

settings = get_settings()

# Configure structured logging for worker
configure_logging(
    json_logs=True,  # Always use JSON for workers
    log_level=settings.log_level,
)

logger = get_logger("cadlift.worker")

# Only create celery app if available and enabled
celery_app = None
if CELERY_AVAILABLE and settings.enable_task_queue:
    celery_app = Celery(
        "cadlift",
        broker=settings.redis_url,
        backend=settings.redis_url,
    )


def _get_celery_task():
    """Get the celery task decorator if available."""
    if celery_app is None:
        raise RuntimeError("Celery not available. Set ENABLE_TASK_QUEUE=true and install celery[redis].")
    return celery_app.task


# Conditionally define the task
if celery_app is not None:
    @celery_app.task(name="process_job")
    def process_job(job_id: str) -> None:
        asyncio.run(process_job_async(job_id))
else:
    def process_job(job_id: str) -> None:
        """Stub function when Celery is not available."""
        raise RuntimeError("Celery not available. Run jobs synchronously or install celery[redis].")


async def process_job_async(job_id: str) -> None:
    async with AsyncSessionLocal() as session:
        job = await session.get(Job, job_id)
        if not job:
            logger.warning("job_not_found", job_id=job_id)
            return

        # Set logging context for this job
        set_request_context(
            job_id=job.id,
            user_id=job.user_id,
        )

        start_time = time.perf_counter()
        try:
            job.status = "processing"
            await session.commit()
            await session.refresh(job)

            logger.info(
                "job_started",
                job_type=job.job_type,
                mode=job.mode,
                input_file_id=job.input_file_id,
            )

            # Run appropriate pipeline
            # Support both old (job_type) and new (job_type+mode) formats
            if job.job_type == "cad":
                await cad.run(job, session)
            elif job.job_type == "image":
                await image.run(job, session)
            elif job.job_type == "prompt":
                await prompt.run(job, session)
            elif job.job_type == "convert":
                if job.mode == "cad":
                    await cad.run(job, session)
                elif job.mode == "image":
                    await image.run(job, session)
                elif job.mode == "prompt":
                    await prompt.run(job, session)
                else:
                    raise ValueError(f"Unsupported mode: {job.mode}")
            else:
                raise ValueError(f"Unsupported job type: {job.job_type}")

            await session.commit()
            duration_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                "job_completed",
                job_type=job.job_type,
                mode=job.mode,
                status=job.status,
                output_file_id=job.output_file_id,
                duration_ms=round(duration_ms, 2),
            )

        except CADLiftError as exc:
            # Handle structured errors
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "job_failed_with_cadlift_error",
                job_type=job.job_type,
                mode=job.mode,
                error_code=exc.error_code,
                error_message=str(exc),
                details=exc.details,
                duration_ms=round(duration_ms, 2),
            )
            job.status = "failed"
            job.error_code = exc.error_code
            job.error_message = str(exc)
            await session.commit()

        except Exception as exc:  # noqa: BLE001
            # Handle unexpected errors
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.exception(
                "job_failed_with_unexpected_error",
                job_type=job.job_type,
                mode=job.mode,
                error_type=type(exc).__name__,
                error_message=str(exc),
                duration_ms=round(duration_ms, 2),
            )
            job.status = "failed"
            job.error_code = "SYS_UNEXPECTED_ERROR"
            job.error_message = str(exc)
            await session.commit()

        finally:
            # Clear logging context
            clear_request_context()
