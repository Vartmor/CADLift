"""
Hybrid pipeline: combine AI-generated mesh with parametric features.

Current approach (safe, local):
- Convert AI + param meshes to Trimesh
- Concatenate geometries (simple union). If no param mesh provided, just process AI mesh.
- Run mesh processing for cleanup/repair/decimation/smoothing
- Export GLB and quality metadata
"""
from __future__ import annotations

import logging
from typing import Any

import trimesh

from app.services.mesh_processor import process_mesh, get_mesh_processor
from app.services.mesh_converter import get_mesh_converter, MeshConversionError

logger = logging.getLogger("cadlift.pipeline.hybrid")


async def run_hybrid_pipeline(
    ai_mesh: bytes,
    ai_format: str = "glb",
    param_mesh: bytes | None = None,
    param_format: str = "glb",
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Hybrid pipeline: merge AI mesh with parametric mesh and process result.

    Args:
        ai_mesh: AI-generated mesh bytes (GLB/OBJ)
        ai_format: AI format
        param_mesh: Optional parametric mesh bytes to combine
        param_format: Parametric mesh format
        params: Hybrid parameters:
            - param_offset: (x, y, z) translation
            - param_scale: float or (x, y, z) scaling
            - ai_scale: float or (x, y, z) scaling for AI mesh
            - boolean_op: "union", "difference", "intersection", or "concatenate" (default)

    Returns:
        {
            "mesh": processed_glb_bytes,
            "quality": quality_metrics_dict,
            "metadata": {...},
            "formats": { "glb": ..., "step": ..., "dxf": ... }
        }
    """
    params = params or {}
    logger.info(
        "Running hybrid pipeline",
        extra={"ai_format": ai_format, "param_present": param_mesh is not None, "params": params},
    )

    ai_tm = _load_as_trimesh(ai_mesh, ai_format)

    # Apply AI scaling if requested
    ai_scale = params.get("ai_scale", None)
    if ai_scale is not None:
        if isinstance(ai_scale, (int, float)):
            ai_tm.apply_scale(ai_scale)
        else:  # tuple/list
            ai_tm.apply_scale(ai_scale)

    combined = ai_tm

    if param_mesh:
        param_tm = _load_as_trimesh(param_mesh, param_format)

        # Apply parametric transformations
        offset = params.get("param_offset", (0.0, 0.0, 0.0))
        if offset != (0.0, 0.0, 0.0):
            param_tm.apply_translation(offset)

        param_scale = params.get("param_scale", None)
        if param_scale is not None:
            if isinstance(param_scale, (int, float)):
                param_tm.apply_scale(param_scale)
            else:  # tuple/list
                param_tm.apply_scale(param_scale)

        # Boolean operation
        boolean_op = params.get("boolean_op", "concatenate")

        if boolean_op == "union":
            try:
                combined = ai_tm.union(param_tm, engine="blender")
            except Exception as exc:
                logger.warning(f"Union operation failed: {exc}, falling back to concatenate")
                combined = trimesh.util.concatenate([ai_tm, param_tm])
        elif boolean_op == "difference":
            try:
                combined = ai_tm.difference(param_tm, engine="blender")
            except Exception as exc:
                logger.warning(f"Difference operation failed: {exc}, falling back to AI mesh only")
                combined = ai_tm
        elif boolean_op == "intersection":
            try:
                combined = ai_tm.intersection(param_tm, engine="blender")
            except Exception as exc:
                logger.warning(f"Intersection operation failed: {exc}, falling back to AI mesh only")
                combined = ai_tm
        else:  # concatenate (default, safe)
            combined = trimesh.util.concatenate([ai_tm, param_tm])

    # Process combined mesh
    processed_glb, quality = await process_mesh(
        mesh_bytes=_export_glb(combined),
        file_type="glb",
    )

    converter = get_mesh_converter()
    formats = {"glb": processed_glb}
    try:
        formats["step"] = converter.convert(processed_glb, "glb", "step")
    except MeshConversionError:
        formats["step"] = b""
    try:
        formats["dxf"] = converter.convert(processed_glb, "glb", "dxf")
    except MeshConversionError:
        formats["dxf"] = b""

    metadata = {
        "pipeline": "hybrid",
        "status": "ready",
        "message": "Hybrid mesh combined and processed",
        "quality_score": quality.overall_score,
        "quality": quality.__dict__,
        "params": params,
    }

    return {
        "mesh": processed_glb,
        "quality": quality.__dict__,
        "metadata": metadata,
        "formats": formats,
    }


def _load_as_trimesh(mesh_bytes: bytes, file_type: str) -> trimesh.Trimesh:
    mesh = trimesh.load(trimesh.util.wrap_as_stream(mesh_bytes), file_type=file_type)
    if isinstance(mesh, trimesh.Scene):
        if len(mesh.geometry) == 0:
            raise ValueError("Scene contains no geometry")
        mesh = next(iter(mesh.geometry.values()))
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(f"Unsupported mesh type: {type(mesh)}")
    return mesh


def _export_glb(mesh: trimesh.Trimesh) -> bytes:
    buf = trimesh.util.wrap_as_stream(b"")
    mesh.export(buf, file_type="glb")
    return buf.getvalue()
