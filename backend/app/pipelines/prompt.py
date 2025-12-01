from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
import logging
import io

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import File as FileModel
from app.models import Job
from app.services.storage import storage_service
from app.pipelines.geometry import build_artifacts
from app.services.llm import llm_service
from app.services.routing import get_routing_service
from app.pipelines.ai import run_ai_pipeline
from app.services.shap_e import get_shap_e_service
from app.core.errors import CADLiftError, ErrorCode
from app.services.mesh_converter import get_mesh_converter, MeshConversionError
from app.services.mesh_processor import process_mesh
from app.services.openai_image import get_openai_image_service, OpenAIImageError
from app.services.triposr import get_triposr_service, TripoSRError
import math
import ezdxf
import cadquery as cq
from io import BytesIO


def _build_gemini_prompt(user_prompt: str) -> str:
    """
    Enrich user prompt for image generation so TripoSG gets a clean reference.

    Emphasizes:
    - Single centered object
    - Neutral background
    - Orthographic view
    - High detail, no text/watermark
    - 1:1 aspect framing
    """
    return (
        "Generate a single, centered object with a clean reference image. "
        "Subject: " + user_prompt.strip() + ". "
        "Style: photorealistic product shot, high detail, sharp focus. "
        "Camera: orthographic front view, straight-on. "
        "Background: neutral gray, no clutter. "
        "Lighting: even studio lighting, soft shadows. "
        "Frame: square 1:1, object fully in frame. "
        "Restrictions: no text, no watermark, no extra props."
    )


logger = logging.getLogger("cadlift.pipeline.prompt")


async def run(job: Job, session: AsyncSession) -> None:
    params = job.params or {}
    prompt_text = (params.get("prompt") or "").strip()
    if not prompt_text:
        raise CADLiftError(ErrorCode.PROMPT_EMPTY, details="Prompt parameter is missing or empty")

    logger.info("Processing prompt job", extra={"job_id": job.id})

    routing = get_routing_service().route(prompt_text)
    logger.info(
        "Routing selection for prompt job",
        extra={"pipeline": routing.pipeline, "category": routing.object_category.value, "confidence": routing.confidence},
    )

    use_ai = params.get("use_ai", True)
    use_gemini_triposg = params.get("use_gemini_triposg", True)

    # New AI path: OpenAI image -> TripoSR mesh (organic/artistic prompts)
    if use_ai and use_gemini_triposg and routing.pipeline == "ai":
        img_service = get_openai_image_service()
        triposr = get_triposr_service()

        if img_service.is_available() and triposr.enabled:
            try:
                logger.info("OpenAI→TripoSR path selected", extra={"job_id": job.id})
                enriched_prompt = _build_gemini_prompt(prompt_text)
                image_bytes = img_service.generate_image(enriched_prompt)

                converter = get_mesh_converter()
                obj_bytes = triposr.generate_from_image(image_bytes)
                glb_bytes = converter.convert(obj_bytes, "obj", "glb")
                target_faces = int(max(20000, min(120000, 20000 + float(params.get("detail", 70)) * 800)))
                quality = None
                try:
                    processed_glb, quality = await process_mesh(glb_bytes, file_type="glb", target_faces=target_faces, min_quality=7.0)
                except Exception as exc:  # pragma: no cover
                    logger.warning(f"Mesh processing skipped: {exc}")
                    processed_glb = glb_bytes

                outputs = {
                    "glb": processed_glb,
                    "obj": converter.convert(processed_glb, "glb", "obj"),
                }
                try:
                    outputs["dxf"] = converter.convert(processed_glb, "glb", "dxf")
                except MeshConversionError:
                    outputs["dxf"] = b""
                if converter.mayo_available:
                    try:
                        outputs["step"] = converter.convert(processed_glb, "glb", "step")
                    except MeshConversionError:
                        outputs["step"] = b""
                else:
                    outputs["step"] = b""

                saved_files: dict[str, FileModel] = {}
                for fmt, data in outputs.items():
                    if not data:
                        continue
                    role = "output" if fmt in {"glb", "dxf", "obj"} else "output_step"
                    fname = f"prompt_model.{fmt}"
                    storage_key, size = storage_service.save_bytes(
                        data,
                        role=role,
                        job_id=job.id,
                        filename=fname,
                    )
                    file_rec = FileModel(
                        user_id=job.user_id,
                        job_id=job.id,
                        role=role,
                        storage_key=storage_key,
                        original_name=fname,
                        mime_type=f"application/{fmt}",
                        size_bytes=size,
                    )
                    session.add(file_rec)
                    await session.flush()
                    saved_files[fmt] = file_rec

                primary = saved_files.get("glb") or saved_files.get("dxf") or saved_files.get("step") or saved_files.get("obj")
                if not primary:
                    raise CADLiftError(ErrorCode.SYS_UNEXPECTED_ERROR, details="AI outputs could not be saved")

                job.output_file_id = primary.id
                job.status = "completed"
                job.error_code = None
                job.error_message = None

                merged_params = dict(params)
                merged_params["ai_metadata"] = {
                    "pipeline": "openai_triposr",
                    "provider": "openai+triposr",
                    "quality_metrics": {
                        "processing_quality_score": getattr(quality, "overall_score", None),
                        "faces": getattr(quality, "face_count", None),
                        "vertices": getattr(quality, "vertex_count", None),
                        "watertight": getattr(quality, "is_watertight", None),
                    },
                }
                if "glb" in saved_files:
                    merged_params["glb_file_id"] = saved_files["glb"].id
                if "step" in saved_files:
                    merged_params["step_file_id"] = saved_files["step"].id
                if "dxf" in saved_files:
                    merged_params["dxf_file_id"] = saved_files["dxf"].id
                if "obj" in saved_files:
                    merged_params["obj_file_id"] = saved_files["obj"].id

                job.params = merged_params
                return

            except (TripoSRError, MeshConversionError, CADLiftError) as exc:
                logger.warning("OpenAI→TripoSR path failed, falling back to parametric", extra={"error": str(exc)})
                use_ai = False  # force parametric fallback
            except OpenAIImageError as exc:
                # If OpenAI hard-fails (quota/HTTP), fall back to parametric.
                logger.warning("OpenAI image generation failed, falling back to parametric", extra={"error": str(exc)})
                use_ai = False

        else:
            logger.warning("OpenAI→TripoSR path unavailable (service disabled); using fallback")
            use_ai = False
    if use_ai and not get_shap_e_service().enabled:
        logger.warning("Shap-E not available; falling back to parametric prompt pipeline")
        use_ai = False

    # Prefer AI path for prompt jobs; if it fails, surface the error instead of silently falling back
    if use_ai:
        ai_result = await run_ai_pipeline(prompt_text, params, source_type="text")
        if ai_result.get("error"):
            raise CADLiftError(ErrorCode.SYS_UNEXPECTED_ERROR, details=str(ai_result["error"]))
        outputs = ai_result.get("outputs") or {}
        if not outputs:
            raise CADLiftError(ErrorCode.SYS_UNEXPECTED_ERROR, details="AI generation returned no outputs")

        saved_files: dict[str, FileModel] = {}
        # Persist available formats
        for fmt, data in outputs.items():
            if not data:
                continue
            role = "output" if fmt in {"glb", "dxf", "obj"} else "output_step"
            fname = f"prompt_model.{fmt}"
            storage_key, size = storage_service.save_bytes(
                data,
                role=role,
                job_id=job.id,
                filename=fname,
            )
            file_rec = FileModel(
                user_id=job.user_id,
                job_id=job.id,
                role=role,
                storage_key=storage_key,
                original_name=fname,
                mime_type=f"application/{fmt}",
                size_bytes=size,
            )
            session.add(file_rec)
            await session.flush()
            saved_files[fmt] = file_rec

        # Pick primary output preference: glb -> dxf -> step -> obj
        primary = saved_files.get("glb") or saved_files.get("dxf") or saved_files.get("step") or saved_files.get("obj")
        if not primary:
            raise CADLiftError(ErrorCode.SYS_UNEXPECTED_ERROR, details="AI outputs could not be saved")

        job.output_file_id = primary.id
        job.status = "completed"
        job.error_code = None
        job.error_message = None

        # Attach metadata/quality for frontend
        merged_params = dict(params)
        merged_params["ai_metadata"] = ai_result.get("metadata")
        merged_params["quality_metrics"] = ai_result.get("metadata", {}).get("quality_metrics")

        # Add file IDs for different formats (Phase 5A: 3D Viewer Integration)
        if "glb" in saved_files:
            merged_params["glb_file_id"] = saved_files["glb"].id
        if "step" in saved_files:
            merged_params["step_file_id"] = saved_files["step"].id
        if "dxf" in saved_files:
            merged_params["dxf_file_id"] = saved_files["dxf"].id
        if "obj" in saved_files:
            merged_params["obj_file_id"] = saved_files["obj"].id

        job.params = merged_params
        return

    instructions = await _generate_instructions(prompt_text, params)
    model = _instructions_to_model(instructions, prompt_text, params)

    json_storage_key, json_size = storage_service.save_bytes(
        json.dumps(model, indent=2).encode("utf-8"),
        role="output_metadata",
        job_id=job.id,
        filename="prompt_model.json",
    )

    json_file = FileModel(
        user_id=job.user_id,
        job_id=job.id,
        role="output_metadata",
        storage_key=json_storage_key,
        original_name="prompt_model.json",
        mime_type="application/json",
        size_bytes=json_size,
    )
    session.add(json_file)
    await session.flush()

    # Get wall thickness from model (default: 200mm for architectural quality)
    wall_thickness = float(model.get("wall_thickness", 200.0))
    detail = float(params.get("detail", 70))
    if model.get("metadata", {}).get("source") == "shapes":
        dxf_bytes, step_bytes = _build_shapes_outputs(model, detail=detail)
    else:
        dxf_bytes, step_bytes = build_artifacts(
            model["contours"],
            model["extrude_height"],
            wall_thickness=wall_thickness
        )
    dxf_storage_key, dxf_size = storage_service.save_bytes(
        dxf_bytes,
        role="output",
        job_id=job.id,
        filename="prompt_model.dxf",
    )
    dxf_file = FileModel(
        user_id=job.user_id,
        job_id=job.id,
        role="output",
        storage_key=dxf_storage_key,
        original_name="prompt_model.dxf",
        mime_type="application/dxf",
        size_bytes=dxf_size,
    )
    session.add(dxf_file)
    await session.flush()

    step_storage_key, step_size = storage_service.save_bytes(
        step_bytes,
        role="output_step",
        job_id=job.id,
        filename="prompt_model.step",
    )
    step_file = FileModel(
        user_id=job.user_id,
        job_id=job.id,
        role="output_step",
        storage_key=step_storage_key,
        original_name="prompt_model.step",
        mime_type="application/step",
        size_bytes=step_size,
    )
    session.add(step_file)
    await session.flush()

    # Generate quality metrics for the output
    quality_metrics = _generate_quality_metrics(instructions, params, model)

    # Preserve the inferred instructions for downstream consumers or debugging.
    merged_params = dict(params)
    merged_params["instructions"] = instructions
    merged_params["step_file_id"] = step_file.id
    merged_params["quality_metrics"] = quality_metrics
    job.params = merged_params
    job.output_file_id = dxf_file.id
    job.status = "completed"
    job.error_code = None
    job.error_message = None


def _generate_quality_metrics(instructions: dict[str, Any], params: dict[str, Any], model: dict[str, Any]) -> dict[str, Any]:
    """
    Generate quality metrics for the generated model.

    Tracks:
    - Number of shapes/rooms generated
    - Advanced features used (tapered, threaded, hollow, filleted)
    - Detail level
    - Model source (shapes vs rooms)

    Args:
        instructions: LLM-generated instructions
        params: User parameters
        model: Generated model

    Returns:
        Quality metrics dictionary
    """
    metrics = {
        "detail_level": float(params.get("detail", 70)),
        "model_source": model.get("metadata", {}).get("source", "unknown"),
    }

    # Shape-specific metrics
    if "shapes" in instructions:
        shapes = instructions["shapes"]
        metrics["shapes_generated"] = len(shapes)

        # Track advanced features used
        advanced_features = {
            "tapered": any(s.get("type") == "tapered_cylinder" for s in shapes),
            "threaded": any(s.get("type") == "thread" for s in shapes),
            "hollow": any(s.get("hollow") for s in shapes),
            "filleted": any(s.get("fillet", 0) > 0 for s in shapes),
            "sweep": any(s.get("type") == "sweep" for s in shapes),
            "revolve": any(s.get("type") == "revolve" for s in shapes),
        }
        metrics["advanced_features_used"] = advanced_features
        metrics["advanced_feature_count"] = sum(advanced_features.values())

        # Track shape type distribution
        shape_types = {}
        for shape in shapes:
            stype = shape.get("type", "unknown")
            shape_types[stype] = shape_types.get(stype, 0) + 1
        metrics["shape_types"] = shape_types

    # Room-specific metrics
    elif "rooms" in instructions:
        rooms = instructions["rooms"]
        metrics["rooms_generated"] = len(rooms)
        metrics["has_custom_polygons"] = any("vertices" in r for r in rooms)
        metrics["has_positioned_rooms"] = any("position" in r for r in rooms)

        # Floor metrics if available
        if "floors" in model.get("metadata", {}):
            metrics["floor_count"] = model["metadata"]["floor_count"]
            metrics["floors"] = model["metadata"]["floors"]

    # Dimension metrics
    metrics["extrude_height"] = float(model.get("extrude_height", 0))
    metrics["wall_thickness"] = float(model.get("wall_thickness", 0))

    # Polygon count (for DXF/STEP complexity)
    if "contours" in model:
        metrics["polygon_count"] = len(model["contours"])
        # Estimate total vertices
        total_vertices = sum(len(poly) for poly in model["contours"])
        metrics["total_vertices"] = total_vertices

    return metrics


def _get_optimal_segments(shape_type: str, detail: float) -> int:
    """
    Calculate optimal segment count for smooth curves based on shape type and detail level.

    Args:
        shape_type: Type of shape (cylinder, tapered_cylinder, thread, etc.)
        detail: Detail level from 0-100

    Returns:
        Optimal segment count (16-160)
    """
    # Base segment counts for different shape types
    base_segments = {
        "cylinder": 24,
        "tapered_cylinder": 32,  # More segments for smooth taper
        "thread": 48,  # High detail for thread appearance
        "revolve": 32,  # Smooth revolution
        "polygon": 16,  # User-defined vertices
        "box": 4,  # No curves
    }

    base = base_segments.get(shape_type, 24)

    # Apply detail multiplier (1.0 to 2.0)
    multiplier = 1.0 + (detail / 100.0)

    optimal = int(base * multiplier)

    # Clamp to reasonable range
    return max(16, min(160, optimal))


def _circle_polygon(radius: float, segments: int = 32) -> list[list[float]]:
    """Approximate a circle as a polygon for downstream extrusion."""
    if radius <= 0:
        raise CADLiftError(ErrorCode.GEO_INVALID_DIMENSIONS, details="Radius must be positive")
    points = []
    for i in range(segments):
        theta = 2 * math.pi * (i / segments)
        points.append([radius * math.cos(theta), radius * math.sin(theta)])
    return points


def _build_shapes_outputs(model: dict[str, Any], detail: float = 70.0) -> tuple[bytes, bytes]:
    """
    Build DXF + STEP from shape instructions using cadquery (solid) and ezdxf (outline).
    Supports box, cylinder, tapered_cylinder, polygon, fillet, hollow, operation (union/diff), thread, revolve, sweep.
    """
    detail = max(0.0, min(detail, 100.0))
    shapes = model["instructions"].get("shapes", [])
    wall_thickness = float(model.get("wall_thickness", 0.0))
    # Build solids
    solid = None
    for idx, shape in enumerate(shapes):
        stype = str(shape.get("type", "")).lower()
        op = str(shape.get("operation", "union")).lower()
        fillet = float(shape.get("fillet", 0.0)) if shape.get("fillet") is not None else 0.0
        hollow = bool(shape.get("hollow", False))
        w_thick = float(shape.get("wall_thickness", wall_thickness))
        pos = shape.get("position") if isinstance(shape.get("position"), (list, tuple)) and len(shape["position"]) == 2 else None
        x_off = float(pos[0]) if pos else 0.0
        y_off = float(pos[1]) if pos else 0.0

        wp = cq.Workplane("XY").transformed(offset=(x_off, y_off, 0))
        if stype == "box":
            w = float(shape.get("width", 0))
            l = float(shape.get("length", 0))
            h = float(shape.get("height", model.get("extrude_height", 100)))
            if w <= 0 or l <= 0 or h <= 0:
                raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"Invalid box dims in shapes[{idx}]")
            obj = wp.box(w, l, h, centered=(True, True, False))
        elif stype == "cylinder":
            r = float(shape.get("radius", 0))
            h = float(shape.get("height", model.get("extrude_height", 100)))
            if r <= 0 or h <= 0:
                raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"Invalid cylinder in shapes[{idx}]")
            obj = wp.circle(r).extrude(h)
            if shape.get("rotate_deg"):
                obj = obj.rotate((0, 0, 0), (0, 0, 1), float(shape.get("rotate_deg")))
        elif stype == "tapered_cylinder":
            bottom_r = float(shape.get("bottom_radius", 0))
            top_r = float(shape.get("top_radius", 0))
            h = float(shape.get("height", model.get("extrude_height", 100)))
            if bottom_r <= 0 or top_r <= 0 or h <= 0:
                raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"Invalid tapered_cylinder in shapes[{idx}]")
            # Create tapered cylinder using loft between two circles
            try:
                obj = (
                    cq.Workplane("XY")
                    .workplane(offset=0)
                    .circle(bottom_r)
                    .workplane(offset=h)
                    .circle(top_r)
                    .loft(combine=True)
                )
                if x_off != 0 or y_off != 0:
                    obj = obj.translate((x_off, y_off, 0))
            except Exception as e:
                logger.warning(f"Tapered cylinder loft failed for shape {idx}: {e}. Using straight cylinder with bottom radius.")
                obj = wp.circle(bottom_r).extrude(h)
            if shape.get("rotate_deg"):
                obj = obj.rotate((0, 0, 0), (0, 0, 1), float(shape.get("rotate_deg")))
        elif stype == "polygon":
            verts = shape.get("vertices")
            h = float(shape.get("height", model.get("extrude_height", 100)))
            if not isinstance(verts, list) or len(verts) < 3 or h <= 0:
                raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"Invalid polygon in shapes[{idx}]")
            obj = wp.polyline([(float(x), float(y)) for x, y in verts]).close().extrude(h)
            if shape.get("rotate_deg"):
                obj = obj.rotate((0, 0, 0), (0, 0, 1), float(shape.get("rotate_deg")))
        elif stype == "thread":
            major_r = float(shape.get("major_radius", 0))
            pitch = float(shape.get("pitch", 0))
            turns = float(shape.get("turns", 0))
            length = float(shape.get("length", model.get("extrude_height", 100)))
            if major_r <= 0 or pitch <= 0 or turns <= 0 or length <= 0:
                raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"Invalid thread in shapes[{idx}]")
            # Try helix; if unavailable, fall back to a solid cylinder (no real thread)
            try:
                minor_r = max(0.1, major_r - pitch * 0.6)
                prof = cq.Workplane("XZ").polyline(
                    [
                        (minor_r, 0),
                        (major_r, pitch / 2),
                        (minor_r, pitch),
                    ]
                ).close()
                helix_edge = cq.Edge.makeHelix(pitch=pitch, height=length, radius=minor_r)
                path_wp = cq.Workplane("XY").newObject([helix_edge]).translate((x_off, y_off, 0))
                obj = prof.sweep(path_wp, multisection=True)
            except Exception as e:
                logger.warning(f"Thread generation failed for shape {idx}: {e}. Using cylinder approximation.")
                obj = wp.circle(major_r).extrude(length)
        elif stype == "revolve":
            prof = shape.get("profile")
            angle = float(shape.get("angle", 360))
            if not isinstance(prof, list) or len(prof) < 2:
                raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"Invalid revolve profile in shapes[{idx}]")
            pts = [(float(x) + x_off, float(y) + y_off) for x, y in prof]
            obj = cq.Workplane("XY").polyline(pts).close().revolve(angle)
        elif stype == "sweep":
            prof = shape.get("profile")
            path = shape.get("path")
            if not isinstance(prof, list) or len(prof) < 2 or not isinstance(path, list) or len(path) < 2:
                raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"Invalid sweep in shapes[{idx}]")
            prof_wp = cq.Workplane("XY").polyline([(float(x), float(y)) for x, y in prof]).close()
            path_wp = cq.Workplane("XY").polyline([(float(x) + x_off, float(y) + y_off) for x, y in path])
            obj = prof_wp.sweep(path_wp, multisection=True)
        else:
            raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"Unsupported shape type: {stype}")

        # Apply hollow shell if requested
        if hollow and w_thick > 0 and stype not in {"thread"}:
            try:
                obj = obj.shell(-w_thick)
            except Exception as e:
                logger.warning(f"Shell operation failed for shape {idx} ({stype}): {e}. Falling back to solid.")
                # Continue with solid object

        # Apply fillet if provided (skip threads)
        if fillet > 0 and stype not in {"thread"}:
            try:
                obj = obj.edges("|Z").fillet(fillet)
            except Exception as e:
                logger.warning(f"Fillet operation failed for shape {idx} ({stype}): {e}. Skipping fillet.")
                # Continue without fillet

        # Combine via union/diff
        solid = obj if solid is None else (solid - obj if op == "diff" else solid.union(obj))

    if solid is None:
        raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details="No valid shapes to build")

    # Export STEP from cadquery solid
    # Export STEP to a temporary file and read bytes
    step_tmp = BytesIO()
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        cq.exporters.export(solid, tmp_path, "STEP")
        with open(tmp_path, "rb") as f:
            step_bytes = f.read()
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    # Build simple DXF outlines (top view)
    doc = ezdxf.new(setup=True)
    msp = doc.modelspace()
    for poly in model["contours"]:
        pts = poly + [poly[0]]
        msp.add_lwpolyline(pts)
    import io
    dxf_stream = io.StringIO()
    doc.write(dxf_stream)
    dxf_bytes = dxf_stream.getvalue().encode()

    return dxf_bytes, step_bytes

async def _generate_instructions(prompt_text: str, params: dict[str, Any]) -> dict[str, Any]:
    """
    Prompt interpreter with hosted LLM support:
    - If params already include structured instructions, trust+validate them.
    - If LLM is enabled, invoke it to parse the prompt.
    - Otherwise, parse simple width/length/height hints locally.
    """
    if "instructions" in params and isinstance(params["instructions"], dict):
        _validate_instruction_schema(params["instructions"])
        return params["instructions"]

    if llm_service.enabled:
        try:
            ai_instructions = await llm_service.generate_instructions(prompt_text)
            _validate_instruction_schema(ai_instructions)
            return ai_instructions
        except Exception as exc:  # noqa: BLE001
            # Fall back to heuristic, but record the error.
            logging.getLogger("cadlift.pipeline.prompt").warning(
                "LLM parse failed; falling back to heuristic", extra={"error": str(exc)}
            )

    width, length = _parse_dimensions(prompt_text)
    extrude_height = _parse_height(prompt_text) or float(params.get("extrude_height", 3000))

    instructions = {
        "rooms": [
            {
                "name": "main_room",
                "width": width,
                "length": length,
            }
        ],
        "corridor_gap": float(params.get("corridor_gap", 1000)),
        "extrude_height": extrude_height,
    }
    _validate_instruction_schema(instructions)
    return instructions


def _parse_dimensions(text: str) -> tuple[float, float]:
    patterns = [
        r"(\d+(?:\.\d+)?)\s*[xX]\s*(\d+(?:\.\d+)?)",
        r"(\d+(?:\.\d+)?)\s*by\s*(\d+(?:\.\d+)?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return float(match.group(1)), float(match.group(2))
    return 5000.0, 5000.0


def _parse_height(text: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)\s*(m|meter|meters)", text, re.IGNORECASE)
    if match:
        return float(match.group(1)) * 1000.0
    return None


def _validate_room_dimensions(room: dict[str, Any], idx: int) -> None:
    """
    Validate that room dimensions are realistic (Phase 2.3.6).

    Args:
        room: Room definition
        idx: Room index for error messages

    Raises:
        ValueError: If dimensions are unrealistic
    """
    if "width" not in room or "length" not in room:
        return  # Custom polygon rooms skip this validation

    width = float(room["width"])
    length = float(room["length"])
    room_name = room.get("name", f"room_{idx}")

    # Minimum dimensions: 1.5m x 1.5m (1500mm) - small closet
    MIN_SIZE = 1500.0
    # Maximum dimensions: 50m x 50m (50000mm) - very large room
    MAX_SIZE = 50000.0

    if width < MIN_SIZE or length < MIN_SIZE:
        raise CADLiftError(
            ErrorCode.PROMPT_INVALID_DIMENSIONS,
            details=f"Room '{room_name}' too small: {width}mm x {length}mm (min: {MIN_SIZE}mm)"
        )

    if width > MAX_SIZE or length > MAX_SIZE:
        raise CADLiftError(
            ErrorCode.PROMPT_INVALID_DIMENSIONS,
            details=f"Room '{room_name}' too large: {width}mm x {length}mm (max: {MAX_SIZE}mm)"
        )

    # Aspect ratio check: warn if one dimension is more than 10x the other
    aspect_ratio = max(width, length) / min(width, length)
    if aspect_ratio > 10:
        logger = logging.getLogger("cadlift.pipeline.prompt")
        logger.warning(
            f"Room '{room_name}' has unusual aspect ratio {aspect_ratio:.1f}:1 "
            f"({width}mm x {length}mm)"
        )


def _detect_room_adjacency(rooms_with_polygons: list[tuple[dict, list[list[float]]]]) -> list[dict[str, Any]]:
    """
    Detect which rooms share walls (Phase 2.3.5).

    Args:
        rooms_with_polygons: List of (room_def, polygon) tuples

    Returns:
        List of adjacency relationships {room1, room2, shared_wall}
    """
    adjacencies = []

    for i in range(len(rooms_with_polygons)):
        for j in range(i + 1, len(rooms_with_polygons)):
            room1_def, poly1 = rooms_with_polygons[i]
            room2_def, poly2 = rooms_with_polygons[j]

            # Check if any edge from poly1 overlaps with any edge from poly2
            # Simple implementation: check if they share 2 consecutive vertices
            for k in range(len(poly1)):
                p1_a = poly1[k]
                p1_b = poly1[(k + 1) % len(poly1)]

                for m in range(len(poly2)):
                    p2_a = poly2[m]
                    p2_b = poly2[(m + 1) % len(poly2)]

                    # Check if edges match (within tolerance)
                    tolerance = 1.0  # 1mm tolerance
                    if (_points_equal(p1_a, p2_a, tolerance) and _points_equal(p1_b, p2_b, tolerance)) or \
                       (_points_equal(p1_a, p2_b, tolerance) and _points_equal(p1_b, p2_a, tolerance)):
                        adjacencies.append({
                            "room1": room1_def.get("name", f"room_{i}"),
                            "room2": room2_def.get("name", f"room_{j}"),
                            "shared_wall": [p1_a, p1_b]
                        })
                        break

    return adjacencies


def _points_equal(p1: list[float], p2: list[float], tolerance: float = 1.0) -> bool:
    """Check if two points are equal within tolerance."""
    return abs(p1[0] - p2[0]) < tolerance and abs(p1[1] - p2[1]) < tolerance


def _instructions_to_model(instructions: dict[str, Any], prompt_text: str, params: dict[str, Any]) -> dict[str, Any]:
    """
    Convert LLM instructions to CADLift model format.
    Supports:
    - Architectural layout (rooms)
    - Object primitives (shapes: box/cylinder/polygon)
    """
    _validate_instruction_schema(instructions)
    has_shapes = instructions.get("shapes")
    has_rooms = instructions.get("rooms")
    prompt_lower = prompt_text.lower()

    # Base defaults
    extrude_height = float(instructions.get("extrude_height", params.get("extrude_height", 3000.0)))
    wall_thickness = float(instructions.get("wall_thickness", params.get("wall_thickness", 200.0)))

    if has_shapes:
        def _shape_span(s: dict[str, Any]) -> float:
            st = str(s.get("type", "")).lower()
            if st == "box":
                return float(s.get("length", 0)) or float(s.get("width", 0)) or 20.0
            if st == "cylinder":
                r = float(s.get("radius", 0))
                return max(1.0, r * 2)
            if st == "tapered_cylinder":
                bottom_r = float(s.get("bottom_radius", 0))
                top_r = float(s.get("top_radius", 0))
                r = max(bottom_r, top_r)
                return max(1.0, r * 2)
            if st == "polygon":
                verts = s.get("vertices", [])
                if isinstance(verts, list) and len(verts) >= 1:
                    ys = [float(v[1]) for v in verts if isinstance(v, list) and len(v) == 2]
                    if ys:
                        return max(ys) - min(ys)
                return 20.0
            if st == "thread":
                r = float(s.get("major_radius", 0))
                return max(1.0, r * 2)
            if st == "revolve":
                prof = s.get("profile", [])
                if isinstance(prof, list) and len(prof) >= 1:
                    ys = [float(v[1]) for v in prof if isinstance(v, list) and len(v) == 2]
                    if ys:
                        return max(ys) - min(ys)
                return 20.0
            if st == "sweep":
                path = s.get("path", [])
                if isinstance(path, list) and len(path) >= 1:
                    ys = [float(v[1]) for v in path if isinstance(v, list) and len(v) == 2]
                    if ys:
                        return max(ys) - min(ys)
                return 20.0
            return 20.0

        polygons: list[list[list[float]]] = []
        auto_offset = 0.0
        max_height = float(instructions.get("extrude_height", params.get("extrude_height", 0.0))) or 0.0
        max_wall = float(instructions.get("wall_thickness", params.get("wall_thickness", 0.0))) or 0.0
        spacing = 20.0  # mm gap between auto-placed shapes
        # Detail level for segment calculation
        detail = float(params.get("detail", 70))
        detail = max(0.0, min(detail, 100.0))
        fillets: list[float] = []
        operations: list[str] = []
        origins: list[tuple[float, float]] = []
        for idx, shape in enumerate(has_shapes):
            stype = str(shape.get("type", "")).lower()
            shape_height = float(shape.get("height", extrude_height))
            if shape_height > 0:
                max_height = max(max_height, shape_height)  # prefer tallest shape height
            if "wall_thickness" in shape:
                max_wall = max(max_wall, float(shape["wall_thickness"]))
            fillets.append(float(shape.get("fillet", 0)))
            operations.append(str(shape.get("operation", "union")).lower())

            # Optional positioning
            pos = shape.get("position")
            pos_x = float(pos[0]) if isinstance(pos, (list, tuple)) and len(pos) == 2 else None
            pos_y = float(pos[1]) if isinstance(pos, (list, tuple)) and len(pos) == 2 else 0.0
            # Auto-align parts contiguously along Y if not explicitly positioned
            if pos_x is None:
                pos_x = 0.0
            if pos is None:
                span = _shape_span(shape)
                pos_y = auto_offset
                auto_offset += span + spacing
            origins.append((pos_x, pos_y))

            if stype == "box":
                w = float(shape.get("width", 0))
                l = float(shape.get("length", 0))
                if w <= 0 or l <= 0:
                    raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"Invalid box dims in shapes[{idx}]")
                hw, hl = w / 2, l / 2
                if pos_x is None:
                    pos_x = auto_offset
                    auto_offset += w + spacing
                polygons.append([
                    [pos_x - hw, pos_y - hl],
                    [pos_x + hw, pos_y - hl],
                    [pos_x + hw, pos_y + hl],
                    [pos_x - hw, pos_y + hl],
                ])
            elif stype == "cylinder":
                r = float(shape.get("radius", 0))
                if r <= 0:
                    raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"Invalid radius in shapes[{idx}]")
                if pos_x is None:
                    pos_x = auto_offset
                    auto_offset += (r * 2) + spacing
                # Use optimized segment count for cylinder
                segments = _get_optimal_segments("cylinder", detail)
                poly = _circle_polygon(r, segments=segments)
                # Offset circle center
                poly = [[x + pos_x, y + pos_y] for x, y in poly]
                polygons.append(poly)
            elif stype == "tapered_cylinder":
                bottom_r = float(shape.get("bottom_radius", 0))
                top_r = float(shape.get("top_radius", 0))
                if bottom_r <= 0 or top_r <= 0:
                    raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"Invalid tapered_cylinder in shapes[{idx}]")
                # For 2D footprint, use the larger radius
                r = max(bottom_r, top_r)
                if pos_x is None:
                    pos_x = auto_offset
                    auto_offset += (r * 2) + spacing
                # Use higher segment count for smooth tapered appearance
                segments = _get_optimal_segments("tapered_cylinder", detail)
                poly = _circle_polygon(r, segments=segments)
                # Offset circle center
                poly = [[x + pos_x, y + pos_y] for x, y in poly]
                polygons.append(poly)
            elif stype == "polygon":
                verts = shape.get("vertices")
                if not isinstance(verts, list) or len(verts) < 3:
                    raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"Invalid vertices in shapes[{idx}]")
                pts = [[float(x), float(y)] for x, y in verts]
                if pos_x is None:
                    # auto place polygon by its bbox width
                    min_x = min(p[0] for p in pts)
                    max_x = max(p[0] for p in pts)
                    width = max_x - min_x
                    pos_x = auto_offset
                    auto_offset += width + spacing
                pts = [[x + pos_x, y + pos_y] for x, y in pts]
                polygons.append(pts)
            elif stype == "sweep":
                prof = shape.get("profile")
                path = shape.get("path")
                if not isinstance(prof, list) or len(prof) < 2 or not isinstance(path, list) or len(path) < 2:
                    raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"Invalid sweep in shapes[{idx}]")
                # Use path extents for auto placement
                min_x = min(p[0] for p in path)
                max_x = max(p[0] for p in path)
                width = max_x - min_x
                if pos_x is None:
                    pos_x = auto_offset
                    auto_offset += width + spacing
                # Handle both 2D [x,y] and 3D [x,y,z] path points
                shifted_path = []
                for pt in path:
                    if len(pt) == 2:
                        shifted_path.append([float(pt[0]) + pos_x, float(pt[1]) + pos_y])
                    elif len(pt) >= 3:
                        # For 3D points, only shift X and Y for 2D footprint
                        shifted_path.append([float(pt[0]) + pos_x, float(pt[1]) + pos_y])
                polygons.append(shifted_path)
            elif stype == "thread":
                # Thread will be built later; use a placeholder contour for DXF
                r = float(shape.get("major_radius", 0))
                length = float(shape.get("length", 0))
                if r <= 0 or length <= 0:
                    raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"Invalid thread in shapes[{idx}]")
                if pos_x is None:
                    pos_x = auto_offset
                    auto_offset += (r * 2) + spacing
                # Use high segment count for thread detail
                segments = _get_optimal_segments("thread", detail)
                poly = _circle_polygon(r, segments=segments)
                poly = [[x + pos_x, y + pos_y] for x, y in poly]
                polygons.append(poly)
            else:
                raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"Unsupported shape type: {stype}")

        extrude_height = max(100.0, min(max_height, 100000.0))
        wall_thickness = max(0.0, min(max_wall, 5000.0))
        return {
            "prompt": prompt_text,
            "instructions": instructions,
            "contours": polygons,
            "extrude_height": extrude_height,
            "wall_thickness": wall_thickness,
            "metadata": {
                "source": "shapes",
                "shape_count": len(polygons),
                "fillets": fillets,
                "operations": operations,
                "origins": origins,
            },
        }

    if not has_rooms or not isinstance(has_rooms, list):
        raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details="No rooms or shapes provided in instructions")

    # Heuristic: if instructions only contain rooms but prompt is likely an object (not building-related), reject.
    building_keywords = [
        "house", "room", "floor", "plan", "apartment", "office", "building",
        "layout", "villa", "kitchen", "bathroom", "living", "bedroom",
        "duvar", "kat", "plan", "oda", "daire",  # Turkish
        "corridor", "hallway", "garage", "basement", "attic", "warehouse",
        "studio", "suite", "closet", "balcony", "terrace", "penthouse"
    ]
    object_keywords = [
        "mug", "cup", "bottle", "container", "glass", "jar", "flask",
        "screw", "bolt", "nut", "washer", "fastener", "nail",
        "adapter", "plug", "connector", "cable", "socket",
        "tool", "wrench", "hammer", "part", "component", "piece",
        "vase", "pot", "bowl", "plate", "dish", "tumbler",
        "cylinder", "box", "sphere", "cone", "tube", "pipe"
    ]
    is_building = any(word in prompt_lower for word in building_keywords)
    is_object = any(word in prompt_lower for word in object_keywords)
    if has_rooms and not has_shapes and not is_building and is_object:
        raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details="Object prompt incorrectly parsed as building. Try more specific description.")

    _validate_instruction_schema(instructions)
    rooms = instructions["rooms"]

    corridor_gap = float(instructions.get("corridor_gap", 1000))

    contours: list[list[list[float]]] = []
    offset_x = 0.0  # For auto-positioned rooms

    # Track rooms by floor for multi-floor support (Phase 2.3.4)
    rooms_by_floor: dict[int, list[tuple[dict, list[list[float]]]]] = {}
    rooms_with_polygons: list[tuple[dict, list[list[float]]]] = []

    for idx, room in enumerate(rooms):
        # Validate room dimensions (Phase 2.3.6)
        _validate_room_dimensions(room, idx)

        # Get floor/level for multi-floor support (Phase 2.3.4)
        floor = int(room.get("floor", room.get("level", 0)))

        # Case 1: Custom polygon (vertices specified)
        if "vertices" in room:
            vertices = room["vertices"]
            if not isinstance(vertices, list) or len(vertices) < 3:
                raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"Room {room.get('name', idx)} vertices must have at least 3 points")

            # Validate and convert vertices to floats
            polygon = []
            for pt_idx, pt in enumerate(vertices):
                if not isinstance(pt, list) or len(pt) != 2:
                    raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"Room {room.get('name', idx)} vertex {pt_idx} must be [x,y]")
                polygon.append([float(pt[0]), float(pt[1])])

            # Offset polygon vertically for multi-floor (Z offset handled in 3D generation)
            rooms_with_polygons.append((room, polygon))
            if floor not in rooms_by_floor:
                rooms_by_floor[floor] = []
            rooms_by_floor[floor].append((room, polygon))

            contours.append(polygon)
            continue

        # Case 2 & 3: Rectangular room (with or without position)
        width = float(room.get("width", 0))
        length = float(room.get("length", 0))
        if width <= 0 or length <= 0:
            raise CADLiftError(ErrorCode.PROMPT_INVALID_DIMENSIONS, details=f"Room {room.get('name', idx)} has invalid dimensions: {width}mm x {length}mm")

        # Check if position is specified
        if "position" in room:
            # Case 2: Positioned rectangular room
            position = room["position"]
            if not isinstance(position, list) or len(position) != 2:
                raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"Room {room.get('name', idx)} position must be [x,y]")

            pos_x = float(position[0])
            pos_y = float(position[1])

            polygon = [
                [pos_x, pos_y],
                [pos_x + width, pos_y],
                [pos_x + width, pos_y + length],
                [pos_x, pos_y + length],
            ]
        else:
            # Case 3: Auto-positioned rectangular room (side-by-side)
            polygon = [
                [offset_x, 0.0],
                [offset_x + width, 0.0],
                [offset_x + width, length],
                [offset_x, length],
            ]
            offset_x += width + corridor_gap

        # Track for adjacency detection (Phase 2.3.5)
        rooms_with_polygons.append((room, polygon))
        if floor not in rooms_by_floor:
            rooms_by_floor[floor] = []
        rooms_by_floor[floor].append((room, polygon))

        contours.append(polygon)

    # Detect room adjacencies (Phase 2.3.5)
    adjacencies = _detect_room_adjacency(rooms_with_polygons)

    metadata = {
        "source": "prompt",
        "room_count": len(contours),
        "floor_count": len(rooms_by_floor),  # Phase 2.3.4
        "floors": sorted(rooms_by_floor.keys()),  # Phase 2.3.4
        "adjacency_count": len(adjacencies),  # Phase 2.3.5
        "adjacencies": adjacencies,  # Phase 2.3.5
    }

    return {
        "prompt": prompt_text,
        "instructions": instructions,
        "contours": contours,
        "extrude_height": extrude_height,
        "wall_thickness": wall_thickness,
        "metadata": metadata,
        "rooms_by_floor": {str(floor): [(room.get("name", f"room_{i}"), poly) for i, (room, poly) in enumerate(rooms)]
                          for floor, rooms in rooms_by_floor.items()},  # Phase 2.3.4
    }


def _validate_instruction_schema(instructions: dict[str, Any]) -> None:
    """
    Validate instruction schema.

    Accepts:
    1. Rectangular rooms: {name, width, length, [position]}
    2. Custom polygon rooms: {name, vertices}
    3. Shapes: {type, ...} (box, cylinder, polygon)
    """
    if not isinstance(instructions, dict):
        raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details="instructions must be an object")

    rooms = instructions.get("rooms")
    shapes = instructions.get("shapes")

    if (not isinstance(rooms, list) or not rooms) and (not isinstance(shapes, list) or not shapes):
        raise CADLiftError(ErrorCode.PROMPT_NO_ROOMS, details="instructions must include non-empty rooms or shapes")

    if isinstance(shapes, list):
        allowed = {"box", "cylinder", "tapered_cylinder", "polygon", "thread", "revolve", "sweep"}
        for idx, shape in enumerate(shapes):
            if not isinstance(shape, dict):
                raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"instructions.shapes[{idx}] must be an object")
            stype = str(shape.get("type", "")).lower()
            if stype not in allowed:
                raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"instructions.shapes[{idx}].type must be one of {sorted(allowed)}")
            if "height" in shape and float(shape["height"]) <= 0:
                raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"instructions.shapes[{idx}].height must be > 0")
            if stype == "box":
                if float(shape.get("width", 0)) <= 0 or float(shape.get("length", 0)) <= 0:
                    raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"instructions.shapes[{idx}] width/length must be > 0")
            if stype == "cylinder":
                if float(shape.get("radius", 0)) <= 0:
                    raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"instructions.shapes[{idx}].radius must be > 0")
            if stype == "tapered_cylinder":
                if float(shape.get("bottom_radius", 0)) <= 0 or float(shape.get("top_radius", 0)) <= 0:
                    raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"instructions.shapes[{idx}] bottom_radius and top_radius must be > 0")
            if stype == "polygon":
                verts = shape.get("vertices")
                if not isinstance(verts, list) or len(verts) < 3:
                    raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"instructions.shapes[{idx}].vertices must have >= 3 points")
            if stype == "thread":
                if float(shape.get("major_radius", 0)) <= 0 or float(shape.get("pitch", 0)) <= 0 or float(shape.get("turns", 0)) <= 0:
                    raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"instructions.shapes[{idx}] thread requires major_radius, pitch, turns > 0")
            if stype == "revolve":
                verts = shape.get("profile")
                if not isinstance(verts, list) or len(verts) < 2:
                    raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"instructions.shapes[{idx}].profile must have >= 2 points")
            if stype == "sweep":
                prof = shape.get("profile")
                path = shape.get("path")
                if not isinstance(prof, list) or len(prof) < 2:
                    raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"instructions.shapes[{idx}].profile must have >= 2 points")
                if not isinstance(path, list) or len(path) < 2:
                    raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"instructions.shapes[{idx}].path must have >= 2 points")

    for idx, room in enumerate(rooms or []):
        if not isinstance(room, dict):
            raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"instructions.rooms[{idx}] must be an object")

        # Must have either (width + length) OR vertices
        has_dimensions = "width" in room and "length" in room
        has_vertices = "vertices" in room

        if not has_dimensions and not has_vertices:
            raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"instructions.rooms[{idx}] must have either (width+length) or vertices")

        # Validate rectangular room
        if has_dimensions:
            if float(room.get("width", 0)) <= 0 or float(room.get("length", 0)) <= 0:
                raise CADLiftError(ErrorCode.PROMPT_INVALID_DIMENSIONS, details=f"instructions.rooms[{idx}] width/length must be > 0")

            # Validate position if present
            if "position" in room:
                pos = room["position"]
                if not isinstance(pos, list) or len(pos) != 2:
                    raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"instructions.rooms[{idx}] position must be [x,y]")

        # Validate custom polygon
        if has_vertices:
            vertices = room["vertices"]
            if not isinstance(vertices, list) or len(vertices) < 3:
                raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details=f"instructions.rooms[{idx}] vertices must have >= 3 points")

    if "corridor_gap" in instructions and float(instructions["corridor_gap"]) < 0:
        raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED, details="corridor_gap must be >= 0")
