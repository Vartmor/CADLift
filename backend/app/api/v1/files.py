from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import deps
from app.core.errors import CADLiftError
from app.core.logging import get_logger
from app.models import File as FileModel
from app.models import Job
from app.pipelines.geometry import export_mesh
from app.services.storage import storage_service

router = APIRouter(prefix="/files", tags=["files"])
logger = get_logger(__name__)

# MIME types for mesh formats
MESH_MIME_TYPES = {
    "obj": "model/obj",
    "stl": "model/stl",
    "ply": "model/ply",
    "off": "model/mesh",
    "gltf": "model/gltf+json",
    "glb": "model/gltf-binary",
}


@router.get("/{file_id}")
async def download_file(
    file_id: str,
    format: Optional[str] = Query(None, description="Export format for output files (obj, stl, ply, glb, gltf, off)"),
    session: AsyncSession = Depends(deps.get_db),
):
    """
    Download a file by ID.

    For output files, supports on-demand format conversion via the `format` parameter.
    Supported formats: OBJ, STL, PLY, GLB, glTF, OFF

    Phase 4: Export Format Expansion
    """
    file = await session.get(FileModel, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    path = storage_service.resolve_path(file.storage_key)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File missing from storage")

    # If no format conversion requested, return file as-is
    if not format:
        filename = file.original_name or f"download.{file.storage_key.split('.')[-1] if '.' in file.storage_key else 'bin'}"
        headers = {
            "Content-Length": str(path.stat().st_size),
            "Content-Disposition": f'attachment; filename="{filename}"',
        }
        return FileResponse(
            path,
            media_type=file.mime_type or "application/octet-stream",
            filename=filename,
            headers=headers,
        )

    # Format conversion only supported for output files
    if file.role != "output":
        raise HTTPException(
            status_code=400,
            detail=f"Format conversion only supported for output files, not {file.role}",
        )

    # Validate format
    format_lower = format.lower()
    if format_lower not in MESH_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {format}. Supported: {', '.join(MESH_MIME_TYPES.keys())}",
        )

    try:
        # Load the job to get metadata
        if not file.job_id:
            raise HTTPException(status_code=400, detail="Output file has no associated job")

        job = await session.get(Job, file.job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Find the model.json metadata file for this job
        stmt = select(FileModel).where(
            FileModel.job_id == job.id, FileModel.role == "output_metadata", FileModel.original_name == "model.json"
        )
        result = await session.execute(stmt)
        metadata_file = result.scalar_one_or_none()

        if not metadata_file:
            raise HTTPException(status_code=404, detail="Job metadata not found (model.json missing)")

        # Load the model.json to get polygons
        metadata_path = storage_service.resolve_path(metadata_file.storage_key)
        if not metadata_path.exists():
            raise HTTPException(status_code=404, detail="Metadata file missing from storage")

        with open(metadata_path, "r") as f:
            model = json.load(f)

        # Extract polygons (handle both 'polygons' and 'contours' keys for different pipelines)
        polygons = model.get("polygons") or model.get("contours")
        if not polygons:
            raise HTTPException(
                status_code=400, detail="No geometry found in job metadata (no polygons or contours)"
            )

        # Get parameters from model
        height = float(model.get("extrude_height", 3000))
        wall_thickness = float(model.get("wall_thickness", 0.0))

        logger.info(
            "format_conversion_requested",
            file_id=file_id,
            job_id=job.id,
            format=format_lower,
            polygon_count=len(polygons),
            height=height,
            wall_thickness=wall_thickness,
        )

        # Generate mesh in requested format
        mesh_bytes = export_mesh(
            polygons=polygons, height=height, wall_thickness=wall_thickness, format=format_lower, tolerance=0.1
        )

        # Generate filename with new extension
        base_name = file.original_name.rsplit(".", 1)[0] if "." in file.original_name else file.original_name
        new_filename = f"{base_name}.{format_lower}"

        logger.info(
            "format_conversion_completed",
            file_id=file_id,
            job_id=job.id,
            format=format_lower,
            output_size=len(mesh_bytes),
        )

        # Return converted file
        return Response(
            content=mesh_bytes,
            media_type=MESH_MIME_TYPES[format_lower],
            headers={"Content-Disposition": f'attachment; filename="{new_filename}"'},
        )

    except CADLiftError as e:
        logger.error("format_conversion_failed", file_id=file_id, error_code=e.code, error=str(e))
        raise HTTPException(status_code=400, detail=f"{e.code}: {e.message}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("format_conversion_error", file_id=file_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Format conversion failed: {str(e)}")
