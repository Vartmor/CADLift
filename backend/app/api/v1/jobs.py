from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import deps
from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.validation import validate_dxf_file, validate_image_file, validate_job_parameters
from app.models import Job, File as FileModel
from app.schemas.job import JobRead
from app.worker import process_job, process_job_async
from app.services.storage import storage_service

logger = get_logger("cadlift.jobs")
settings = get_settings()

router = APIRouter(prefix="/jobs", tags=["jobs"])


def serialize_job(job: Job) -> JobRead:
    return JobRead(
        id=job.id,
        job_type=job.job_type,
        mode=job.mode,
        status=job.status,
        progress=job.progress,  # Include progress in response
        params=job.params,
        error_code=job.error_code,
        error_message=job.error_message,
        input_file_id=job.input_file_id,
        output_file_id=job.output_file_id,
        created_at=job.created_at,
        updated_at=job.updated_at,
        completed_at=job.completed_at,
    )


@router.post("", response_model=JobRead, status_code=status.HTTP_201_CREATED)
async def create_job_endpoint(
    job_type: str = Form(...),
    mode: str = Form(...),
    params: str | None = Form(None),
    upload: UploadFile | None = File(None),
    session: AsyncSession = Depends(deps.get_db),
):
    # Parse parameters
    job_params = {}
    if params:
        try:
            job_params = json.loads(params)
        except ValueError:
            raise HTTPException(status_code=400, detail="params must be valid JSON")

    # Phase 3.4: Validate parameters
    is_valid, error_msg = validate_job_parameters(job_type, job_params)
    if not is_valid:
        logger.warning("parameter_validation_failed", job_type=job_type, error=error_msg)
        raise HTTPException(status_code=400, detail=f"Invalid parameters: {error_msg}")

    job = Job(job_type=job_type, mode=mode, status="queued", params=job_params)
    session.add(job)
    await session.flush()

    max_bytes = int(settings.max_upload_mb * 1024 * 1024)
    # Allowed MIME types - browsers may report various types for DXF/DWG files
    allowed_mimes = {
        "application/dxf", 
        "image/vnd.dxf",
        "image/x-dxf",
        "application/x-dxf",
        "application/x-dwg",  # DWG files
        "image/vnd.dwg",
        "image/x-dwg",
        "application/acad",
        "application/autocad_dwg",
        "text/plain",  # Some browsers report DXF as text
        "application/octet-stream",  # Generic binary
        "image/png", 
        "image/jpeg", 
        "image/jpg"
    }
    # Also allow by file extension for DXF/DWG
    cad_extensions = {".dxf", ".dwg"}
    image_extensions = {".png", ".jpg", ".jpeg"}

    if upload:
        filename_lower = (upload.filename or "").lower()
        file_ext = filename_lower[filename_lower.rfind("."):] if "." in filename_lower else ""
        
        # Check if MIME type is allowed OR file extension is allowed
        mime_allowed = upload.content_type in allowed_mimes
        ext_allowed = file_ext in cad_extensions or file_ext in image_extensions
        
        if not mime_allowed and not ext_allowed:
            logger.warning("unsupported_file_type", content_type=upload.content_type, filename=upload.filename)
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {upload.content_type}")

        # Phase 3.4: Validate uploaded file BEFORE saving
        file_data = await upload.read()
        await upload.seek(0)  # Reset for later reading

        # Validate based on file extension (more reliable than MIME type)
        is_dxf = file_ext == ".dxf"
        is_dwg = file_ext == ".dwg"
        is_image = file_ext in image_extensions
        
        if is_dxf:
            is_valid, error_msg = validate_dxf_file(file_data, upload.filename or "upload.dxf")
            if not is_valid:
                logger.warning("dxf_validation_failed", filename=upload.filename, error=error_msg)
                raise HTTPException(status_code=400, detail=f"Invalid DXF file: {error_msg}")
            logger.info("dxf_validation_passed", filename=upload.filename)
        
        elif is_dwg:
            # DWG files are validated during conversion in the pipeline
            logger.info("dwg_file_accepted", filename=upload.filename)

        elif is_image:
            is_valid, error_msg = validate_image_file(file_data, upload.filename or "upload.png")
            if not is_valid:
                logger.warning("image_validation_failed", filename=upload.filename, error=error_msg)
                raise HTTPException(status_code=400, detail=f"Invalid image file: {error_msg}")
            logger.info("image_validation_passed", filename=upload.filename)

        # File is valid, proceed with storage
        try:
            storage_key, size = await storage_service.save_upload(
                upload, role="input", job_id=job.id, max_bytes=max_bytes
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        file_record = FileModel(
            user_id=None,
            job_id=job.id,
            role="input",
            storage_key=storage_key,
            original_name=upload.filename or "upload.bin",
            mime_type=upload.content_type,
            size_bytes=size,
        )
        session.add(file_record)
        await session.flush()
        job.input_file_id = file_record.id

    await session.commit()
    await session.refresh(job)
    logger.info(
        "Job queued",
        extra={
            "job_id": job.id,
            "job_type": job.job_type,
            "mode": job.mode,
            "input_file_id": job.input_file_id,
        },
    )
    if settings.enable_task_queue:
        process_job.delay(job.id)
    else:
        # Run in background - don't block the response
        import asyncio
        asyncio.create_task(process_job_async(job.id))
    return serialize_job(job)


@router.get("", response_model=list[JobRead])
async def list_jobs(session: AsyncSession = Depends(deps.get_db)):
    from datetime import datetime, timedelta
    
    # Auto-cleanup: mark stuck processing jobs as failed (older than 10 minutes)
    timeout_threshold = datetime.utcnow() - timedelta(minutes=10)
    stuck_jobs_result = await session.execute(
        select(Job).where(
            Job.status.in_(["processing", "queued"]),
            Job.updated_at < timeout_threshold
        )
    )
    stuck_jobs = stuck_jobs_result.scalars().all()
    for job in stuck_jobs:
        job.status = "failed"
        job.error_message = "Job timed out (stuck for more than 10 minutes)"
        logger.warning(f"Auto-marked stuck job {job.id} as failed")
    
    if stuck_jobs:
        await session.commit()
    
    result = await session.execute(select(Job).order_by(Job.created_at.desc()))
    jobs = result.scalars().all()
    return [serialize_job(job) for job in jobs]


@router.get("/{job_id}", response_model=JobRead)
async def get_job(job_id: str, session: AsyncSession = Depends(deps.get_db)):
    result = await session.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return serialize_job(job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: str, session: AsyncSession = Depends(deps.get_db)):
    """Delete a job and its associated files."""
    result = await session.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Delete associated files
    files_result = await session.execute(select(FileModel).where(FileModel.job_id == job_id))
    files = files_result.scalars().all()
    for file in files:
        try:
            storage_service.delete(file.storage_key)
        except Exception as e:
            logger.warning(f"Failed to delete file {file.storage_key}: {e}")
        await session.delete(file)
    
    await session.delete(job)
    await session.commit()
    logger.info(f"Deleted job {job_id} and {len(files)} associated files")


@router.post("/{job_id}/cancel", response_model=JobRead)
async def cancel_job(job_id: str, session: AsyncSession = Depends(deps.get_db)):
    """Cancel a running or queued job."""
    result = await session.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status in ("completed", "failed", "cancelled"):
        raise HTTPException(status_code=400, detail=f"Job is already {job.status}")
    
    job.status = "cancelled"
    job.error_message = "Job cancelled by user"
    await session.commit()
    logger.info(f"Cancelled job {job_id}")
    return serialize_job(job)
