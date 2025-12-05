"""
AI-based 3D generation pipeline.

Handles text-to-3D and image-to-3D generation using AI services.
"""
from __future__ import annotations

import logging
from typing import Any
from io import BytesIO

from app.services.shap_e import get_shap_e_service, ShapEAPIError
from app.services.mesh_converter import get_mesh_converter, MeshConversionError
from app.services.triposr import get_triposr_service, TripoSRError
from app.services.mesh_processor import process_mesh, get_mesh_processor

logger = logging.getLogger("cadlift.pipeline.ai")


async def run_ai_pipeline(
    prompt: str,
    params: dict[str, Any],
    source_type: str = "text"
) -> dict[str, Any]:
    """
    Run AI generation pipeline.

    Args:
        prompt: User's text prompt
        params: Pipeline parameters (detail level, etc.)
        source_type: 'text' or 'image'

    Returns:
        Dictionary with:
        - metadata: Pipeline info and quality metrics
        - error: Error info if generation failed
        - fallback_used: Whether fallback to parametric was used

    Note: When Shap-E/TripoSR are available locally, this returns converted
    meshes + quality metrics. If the service is missing, it returns metadata.
    """
    logger.info(
        "Starting AI pipeline",
        extra={
            "prompt": prompt[:100],
            "source_type": source_type,
            "detail": params.get("detail", 70)
        }
    )

    try:
        if source_type == "image":
            triposr = get_triposr_service()
            if not triposr.enabled:
                logger.warning("Image-to-3D service not enabled, image pipeline unavailable")
                return {
                    "metadata": {
                        "pipeline": "ai",
                        "source_type": source_type,
                        "status": "service_not_available",
                        "message": "Install TripoSR dependencies and clone docs/useful_projects/TripoSR",
                    },
                    "error": "TripoSR not installed",
                    "fallback_used": False,
                }

            # Expect image bytes in params["image_bytes"]; otherwise fall back to prompt route
            image_bytes = params.get("image_bytes")
            if not image_bytes:
                logger.warning("No image bytes provided for TripoSR; falling back to metadata only")
                return {
                    "metadata": {
                        "pipeline": "ai",
                        "source_type": source_type,
                        "status": "no_image",
                        "message": "Provide image_bytes in params for TripoSR image-to-3D",
                    },
                    "error": "image_bytes missing",
                    "fallback_used": False,
                }

            # Free GPU memory before loading TripoSR (SD may be loaded from a previous prompt job)
            try:
                from app.services.stable_diffusion import get_stable_diffusion_service
                sd_service = get_stable_diffusion_service()
                if sd_service._pipe is not None:
                    logger.info("Unloading Stable Diffusion to free GPU memory for TripoSR")
                    sd_service.unload()
            except Exception as e:
                logger.debug(f"SD unload skipped: {e}")

            obj_bytes = triposr.generate_from_image(image_bytes)
            converter = get_mesh_converter()

            formats = {
                "obj": obj_bytes,
                "glb": converter.convert(obj_bytes, "obj", "glb"),
            }
            # Optional mesh processing (GLB path)
            processed_glb = formats["glb"]
            quality = None
            try:
                processed_glb, quality = await process_mesh(processed_glb, file_type="glb")
            except Exception as exc:  # pragma: no cover
                logger.warning(f"Mesh processing skipped: {exc}")
            formats["glb"] = processed_glb

            try:
                formats["dxf"] = converter.convert(processed_glb, "glb", "dxf")
            except MeshConversionError:
                formats["dxf"] = b""
            try:
                formats["step"] = converter.convert(processed_glb, "glb", "step")
            except MeshConversionError:
                formats["step"] = b""

            return {
                "metadata": {
                    "pipeline": "ai",
                    "source_type": source_type,
                    "provider": "triposr_local",
                    "status": "completed",
                    "message": "Image-to-3D generation complete",
                    "quality_metrics": {
                        "model_source": "ai",
                        "estimated_generation_time": "<30s (GPU) or <2 min (CPU) when deps installed",
                        "estimated_cost": "$0.00 (local TripoSR)",
                        "processing_quality_score": quality.overall_score if quality else None,
                        "faces": quality.face_count if quality else None,
                        "vertices": quality.vertex_count if quality else None,
                        "watertight": quality.is_watertight if quality else None,
                    },
                },
                "outputs": formats,
                "error": None,
                "fallback_used": False,
            }

        # Text path: Shap-E
        shap_e = get_shap_e_service()

        if not shap_e.enabled:
            logger.error("Shap-E service not enabled; install from docs/useful_projects/shap-e-main with pip install -e .")
            raise ShapEAPIError("Shap-E service not enabled; install local Shap-E package")

        # Text pipeline: generate with Shap-E, convert, then quality-process
        detail = float(params.get("detail", 70))
        guidance = float(params.get("guidance_scale", 15.0))
        steps = int(params.get("num_steps", 64))
        target_faces = int(max(20000, min(120000, 20000 + detail * 800)))  # scale target faces with detail

        converter = get_mesh_converter()
        quality = None

        try:
            # 1) Generate raw mesh (PLY) with Shap-E
            ply_bytes = await shap_e.generate_from_text(
                prompt,
                guidance_scale=guidance,
                num_steps=steps,
            )

            # 2) Convert to GLB first (authoritative format)
            glb_bytes = converter.convert(ply_bytes, "ply", "glb")

            # 3) Mesh cleanup/decimate/smooth/repair with quality scoring
            try:
                processed_glb, quality = await process_mesh(
                    glb_bytes,
                    file_type="glb",
                    target_faces=target_faces,
                    min_quality=7.0,
                )
            except Exception as exc:  # pragma: no cover - best effort fallback
                logger.warning(f"Mesh processing skipped due to error: {exc}")
                processed_glb = glb_bytes
                quality = None

            # 4) Convert processed GLB to other formats
            outputs = {
                "glb": processed_glb,
                "obj": converter.convert(processed_glb, "glb", "obj"),
            }
            try:
                outputs["dxf"] = converter.convert(processed_glb, "glb", "dxf")
            except MeshConversionError:
                outputs["dxf"] = b""
            try:
                outputs["step"] = converter.convert(processed_glb, "glb", "step")
            except MeshConversionError:
                outputs["step"] = b""

            return {
                "metadata": {
                    "pipeline": "ai",
                    "source_type": source_type,
                    "provider": "shap_e_local",
                    "prompt": prompt,
                    "optimized_prompt": shap_e._optimize_prompt(prompt),
                    "detail_level": detail,
                    "status": "completed",
                    "message": "AI generation complete",
                    "quality_metrics": {
                        "model_source": "ai",
                        "detail_level": detail,
                        "estimated_generation_time": "30-60s (GPU) or 2-5 min (CPU)",
                        "estimated_cost": "$0.00 (local models)",
                        "processing_quality_score": quality.overall_score if quality else None,
                        "faces": quality.face_count if quality else None,
                        "vertices": quality.vertex_count if quality else None,
                        "watertight": quality.is_watertight if quality else None,
                    },
                },
                "outputs": outputs,
                "error": None,
                "fallback_used": False,
            }

        except (ShapEAPIError, MeshConversionError) as e:
            logger.error(f"AI generation failed: {e}")
            return {
                "metadata": {
                    "pipeline": "ai",
                    "source_type": source_type,
                    "provider": "shap_e_local",
                    "status": "failed",
                    "message": str(e),
                    "quality_metrics": None,
                },
                "error": str(e),
                "outputs": None,
                "fallback_used": True,
            }

    except (ShapEAPIError, TripoSRError) as e:
        logger.error(f"AI generation failed: {e}")
        return {
            "metadata": {
                "pipeline": "ai",
                "status": "failed",
                "error": str(e),
                "quality_metrics": None,
            },
            "error": str(e),
            "fallback_used": False
        }
    except Exception as e:
        logger.error(f"Unexpected error in AI pipeline: {e}")
        return {
            "metadata": {
                "pipeline": "ai",
                "status": "error",
                "error": str(e),
                "quality_metrics": None,
            },
            "error": str(e),
            "fallback_used": False
        }


async def generate_from_text_ai(
    prompt: str,
    guidance_scale: float = 15.0,
    num_steps: int = 64
) -> bytes | None:
    """
    Generate 3D mesh from text using AI.

    This is a helper function that will be called when API is integrated.

    Returns:
        GLB file bytes or None if failed
    """
    try:
        shap_e = get_shap_e_service()

        if not shap_e.enabled:
            logger.warning("Shap-E service not enabled")
            return None

        # Generate mesh
        glb_bytes = await shap_e.generate_from_text(
            prompt,
            guidance_scale=guidance_scale,
            num_steps=num_steps
        )

        return glb_bytes

    except ShapEAPIError as e:
        logger.error(f"AI generation failed: {e}")
        return None


async def convert_ai_mesh_to_formats(glb_bytes: bytes) -> dict[str, bytes]:
    """
    Convert AI-generated mesh to CADLift output formats.

    Args:
        glb_bytes: GLB file bytes from AI service

    Returns:
        Dictionary with format conversions:
        - 'glb': Original GLB
        - 'step': STEP file
        - 'dxf': DXF file
        - 'obj': OBJ file
    """
    converter = get_mesh_converter()

    try:
        # Convert to various formats
        formats = {
            'glb': glb_bytes,
            'dxf': converter.convert(glb_bytes, 'glb', 'dxf'),
            'obj': converter.convert(glb_bytes, 'glb', 'obj'),
        }

        # STEP conversion (may need enhancement)
        try:
            formats['step'] = converter.convert(glb_bytes, 'glb', 'step')
        except MeshConversionError as e:
            logger.warning(f"STEP conversion failed: {e}")
            formats['step'] = b""

        logger.info(
            "Mesh converted to multiple formats",
            extra={
                "formats": list(formats.keys()),
                "sizes": {k: len(v) for k, v in formats.items() if v}
            }
        )

        return formats

    except Exception as e:
        logger.error(f"Format conversion failed: {e}")
        raise MeshConversionError(f"Failed to convert AI mesh: {e}")
