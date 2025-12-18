from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import File as FileModel
from app.models import Job
from app.services.storage import storage_service
from app.pipelines.geometry import build_artifacts
from app.services.vision import vision_service
from app.core.errors import CADLiftError, ErrorCode
from app.services.triposg import get_triposg_service, TripoSGError
from app.services.mesh_converter import get_mesh_converter, MeshConversionError
from app.services.mesh_processor import process_mesh
from app.pipelines.ai import run_ai_pipeline
import logging

logger = logging.getLogger("cadlift.pipeline.image")

async def run(job: Job, session: AsyncSession) -> None:
    # Helper to update job progress
    async def update_progress(progress: int) -> None:
        job.progress = min(100, max(0, progress))
        await session.commit()

    if not job.input_file_id:
        raise CADLiftError(ErrorCode.SYS_FILE_NOT_FOUND, details="Job has no input_file_id")

    input_file = await session.get(FileModel, job.input_file_id)
    if not input_file:
        raise CADLiftError(ErrorCode.SYS_FILE_NOT_FOUND, details=f"File {job.input_file_id} not found in database")

    input_path = storage_service.resolve_path(input_file.storage_key)
    logger.info("Processing image job", extra={"job_id": job.id, "input": input_path})
    await update_progress(5)  # Starting

    params = job.params or {}
    merged_params = dict(params) # Initialize early to avoid scope errors
    ai_metadata: dict | None = None

    # Determine mode-specific flags
    is_precision_mode = (job.mode == "image_to_precision")
    is_2d_mode = (job.mode == "image_to_2d")

    # Optional: TripoSG direct image-to-3D
    # Skip if we are in a precision (engineering) mode or 2D mode
    if bool(params.get("use_triposg", False)) and not (is_precision_mode or is_2d_mode):
        triposg = get_triposg_service()
        if triposg.is_available():
            try:
                image_bytes = input_path.read_bytes()
                target_faces = int(max(20000, min(120000, 20000 + float(params.get("detail", 70)) * 800)))
                glb_bytes = triposg.generate_mesh(image_bytes, faces=target_faces)
                converter = get_mesh_converter()
                quality = None
                try:
                    processed_glb, quality = await process_mesh(glb_bytes, file_type="glb", target_faces=target_faces)
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
                try:
                    outputs["step"] = converter.convert(processed_glb, "glb", "step")
                except MeshConversionError:
                    outputs["step"] = b""

                saved_files: dict[str, FileModel] = {}
                for fmt, data in outputs.items():
                    if not data:
                        continue
                    role = "output" if fmt in {"glb", "dxf", "obj"} else "output_step"
                    filename = f"image_model.{fmt}"
                    storage_key, size = storage_service.save_bytes(
                        data,
                        role=role,
                        job_id=job.id,
                        filename=filename,
                    )
                    file_rec = FileModel(
                        user_id=job.user_id,
                        job_id=job.id,
                        role=role,
                        storage_key=storage_key,
                        original_name=filename,
                        mime_type=f"application/{fmt}",
                        size_bytes=size,
                    )
                    session.add(file_rec)
                    await session.flush()
                    saved_files[fmt] = file_rec

                primary = saved_files.get("glb") or saved_files.get("dxf") or saved_files.get("step") or saved_files.get("obj")
                if primary:
                    job.output_file_id = primary.id

                merged_params = dict(params)
                merged_params["ai_metadata"] = {
                    "pipeline": "triposg",
                    "provider": "triposg_local",
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
                job.status = "completed"
                job.error_code = None
                job.error_message = None
                return
            except (TripoSGError, MeshConversionError) as exc:
                logger.warning("TripoSG path failed, falling back to other pipelines", extra={"error": str(exc)})
        else:
            logger.warning("TripoSG path requested but service unavailable; continuing to other pipelines")

    # Phase 6: Try TripoSR image-to-3D when enabled (same approach as prompt.py)
    # Skip if mode is image_to_2d OR image_to_precision
    use_triposr = bool(params.get("use_triposr", True)) and not (is_2d_mode or is_precision_mode)
    
    if use_triposr:
        from app.services.triposr import get_triposr_service, TripoSRError
        from app.services.mesh_converter import get_mesh_converter, MeshConversionError
        from app.services.mesh_processor import process_mesh
        import gc
        import inspect
        
        triposr = get_triposr_service()
        
        if triposr.is_available():
            try:
                # CRITICAL: Free GPU memory before loading TripoSR
                # This prevents the crash that happens when other models are loaded
                try:
                    import torch
                    torch.cuda.empty_cache()
                    gc.collect()
                    logger.info("Cleared GPU cache before TripoSR")
                except Exception:
                    pass
                await update_progress(10)  # GPU cleanup done
                
                # Also unload Stable Diffusion if it was loaded from a previous job
                try:
                    from app.services.stable_diffusion import get_stable_diffusion_service
                    sd_service = get_stable_diffusion_service()
                    if sd_service._pipe is not None:
                        logger.info("Unloading Stable Diffusion to free GPU memory")
                        sd_service.unload()
                except Exception:
                    pass
                
                image_bytes = input_path.read_bytes()
                target_faces = int(max(20000, min(120000, 20000 + float(params.get("detail", 70)) * 800)))
                
                await update_progress(20)  # Starting 3D generation
                logger.info("Starting TripoSR image-to-3D generation")
                obj_bytes = triposr.generate_from_image(image_bytes)
                await update_progress(50)  # 3D generation complete
                logger.info("TripoSR generation complete, converting formats")
                
                converter = get_mesh_converter()
                glb_bytes = converter.convert(obj_bytes, "obj", "glb")
                
                # Process mesh for quality
                quality = None
                try:
                    pm_result = process_mesh(glb_bytes, file_type="glb", target_faces=target_faces, min_quality=7.0)
                    if inspect.isawaitable(pm_result):
                        processed_glb, quality = await pm_result
                    else:
                        processed_glb, quality = pm_result
                except Exception as exc:
                    logger.warning(f"Mesh processing skipped: {exc}")
                    processed_glb = glb_bytes
                await update_progress(70)  # Mesh processing done
                
                # Generate all output formats
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
                await update_progress(85)  # Format conversion done
                
                # Save output files
                saved_files: dict[str, FileModel] = {}
                for fmt, data in outputs.items():
                    if not data:
                        continue
                    role = "output" if fmt in {"glb", "dxf", "obj"} else "output_step"
                    filename = f"image_model.{fmt}"
                    storage_key, size = storage_service.save_bytes(
                        data,
                        role=role,
                        job_id=job.id,
                        filename=filename,
                    )
                    file_rec = FileModel(
                        user_id=job.user_id,
                        job_id=job.id,
                        role=role,
                        storage_key=storage_key,
                        original_name=filename,
                        mime_type=f"application/{fmt}",
                        size_bytes=size,
                    )
                    session.add(file_rec)
                    await session.flush()
                    saved_files[fmt] = file_rec
                
                primary = saved_files.get("glb") or saved_files.get("dxf") or saved_files.get("step") or saved_files.get("obj")
                if primary:
                    job.output_file_id = primary.id
                
                merged_params = dict(params)
                merged_params["ai_metadata"] = {
                    "pipeline": "triposr_direct",
                    "provider": "triposr_local",
                    "quality_metrics": {
                        "processing_quality_score": getattr(quality, "overall_score", None) if quality else None,
                        "faces": getattr(quality, "face_count", None) if quality else None,
                        "vertices": getattr(quality, "vertex_count", None) if quality else None,
                        "watertight": getattr(quality, "is_watertight", None) if quality else None,
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
                job.status = "completed"
                job.progress = 100  # Complete
                job.error_code = None
                job.error_message = None
                logger.info("Image-to-3D completed successfully")
                return
                
            except (TripoSRError, MeshConversionError) as exc:
                logger.warning("TripoSR image-to-3D failed, falling back to parametric", extra={"error": str(exc)})
            except Exception as exc:
                logger.warning("TripoSR unexpected error, falling back to parametric", extra={"error": str(exc)})
    
    # Phase 7: Smart Blueprint Processing (Vision AI)
    # If not forced-2D, try to interpret the drawing as a precision part
    # Default to True for now as this is a new feature
    # FORCE vision if we are in precision mode
    use_vision = bool(params.get("use_vision", True)) or is_precision_mode
    
    # Try vision if we have LLM service enabled and we are in 2D or 3D mode
    if use_vision:
        try:
            from app.services.llm import llm_service
            if llm_service.enabled:
                logger.info("Attempting Smart Blueprint Processing via Vision AI")
                await update_progress(15)

                # UNIFIED PIPELINE: If Precision Mode, convert Image -> Text -> CAD
                if is_precision_mode:
                    logger.info("Precision Mode: Using Unified Image-to-Text-to-CAD pipeline")
                    image_bytes = input_path.read_bytes()
                    
                    # 1. Vision AI: Generate Text Prompt
                    generated_prompt = await llm_service.describe_image(
                        image_bytes,
                        prompt_text=params.get("prompt")
                    )
                    logger.info(f"Generated CAD Prompt from Image: {generated_prompt}")
                    
                    # 2. Update params
                    merged_params["generated_prompt"] = generated_prompt
                    merged_params["vision_pipeline"] = "text_bridge"
                    
                    # 3. Delegate to Prompt Pipeline (SolidPython)
                    from app.pipelines.prompt import run_precision_cad
                    await run_precision_cad(job, session, generated_prompt, merged_params)
                    return
                
                # Check for cached instructions from params (e.g. from retry)
                vision_instructions = params.get("vision_instructions")
                
                if not vision_instructions:
                    image_bytes = input_path.read_bytes()
                    vision_instructions = await llm_service.generate_from_image(
                        image_bytes, 
                        prompt_text=params.get("prompt") # Optional hint from user
                    )
                
                if vision_instructions:
                    logger.info("Vision analysis successful, building precision model")
                    await update_progress(30)
                    
                    from app.services.parametric_service import instructions_to_model
                    
                    # Convert instructions to model using shared logic
                    # Provide defaults from params
                    model = instructions_to_model(vision_instructions, "", params)
                    
                    # Ensure metadata reflects vision source
                    model["metadata"]["source"] = "vision_ai"
                    
                    if ai_metadata is None:
                        ai_metadata = {}
                    ai_metadata["vision_pipeline"] = True
                    # Also store instructions in params for debugging/retries
                    merged_params["vision_instructions"] = vision_instructions
                    
                    # Skip local contour extraction since we have precision model
                    # But we need to update job status here because we skip _generate_model
                    
                    # Continue to artifact generation (lines 294+) using this model
                    # We jump to line 294 by breaking out of fallback logic?
                    # The code structure below calls _generate_model if we don't return here.
                    # But _generate_model is for pixel tracing.
                    # So we should use this model and proceed to artifact generation.
                    pass 
                else:
                    logger.info("Vision AI returned no instructions, falling back")
                    model = await _generate_model(input_path, job)
            else:
                model = await _generate_model(input_path, job) # No LLM
        except Exception as e:
            logger.warning(f"Smart Blueprint Processing failed: {e}", extra={"error": str(e)})
            # Fallback to standard pixel tracing
            model = await _generate_model(input_path, job)
    else:
        model = await _generate_model(input_path, job)

    # Ensure model is valid before proceeding
    if not model:
         # Should be caught by exception handlers but safe guard
         model = await _generate_model(input_path, job)

    json_storage_key, json_size = storage_service.save_bytes(
        json.dumps(model, indent=2).encode("utf-8"),
        role="output_metadata",
        job_id=job.id,
        filename="image_model.json",
    )
    json_file = FileModel(
        user_id=job.user_id,
        job_id=job.id,
        role="output_metadata",
        storage_key=json_storage_key,
        original_name="image_model.json",
        mime_type="application/json",
        size_bytes=json_size,
    )
    session.add(json_file)
    await session.flush()

    # Get wall thickness from model
    # For precision/mechanical parts, default to 0 (solid) if not specified
    # For architectural/floor plans, default to 200mm
    default_thickness = 0.0 if is_precision_mode else 200.0
    wall_thickness = float(model.get("wall_thickness", default_thickness))
    
    only_2d = model.get("only_2d", False)
    dxf_bytes, step_bytes = build_artifacts(
        model["contours"],
        model["extrude_height"],
        wall_thickness=wall_thickness,
        only_2d=only_2d,
        operations=model.get("metadata", {}).get("operations")
    )
    dxf_storage_key, dxf_size = storage_service.save_bytes(
        dxf_bytes,
        role="output",
        job_id=job.id,
        filename="image_model.dxf",
    )
    dxf_file = FileModel(
        user_id=job.user_id,
        job_id=job.id,
        role="output",
        storage_key=dxf_storage_key,
        original_name="image_model.dxf",
        mime_type="application/dxf",
        size_bytes=dxf_size,
    )
    session.add(dxf_file)
    await session.flush()

    step_storage_key, step_size = storage_service.save_bytes(
        step_bytes,
        role="output_step",
        job_id=job.id,
        filename="image_model.step",
    )
    step_file = FileModel(
        user_id=job.user_id,
        job_id=job.id,
        role="output_step",
        storage_key=step_storage_key,
        original_name="image_model.step",
        mime_type="application/step",
        size_bytes=step_size,
    )
    session.add(step_file)
    await session.flush()

    # Generate GLB for 3D Viewer (Visualization Only)
    # This allows the frontend to show a 3D preview even in 2D mode
    glb_file = None
    try:
        from app.pipelines.geometry import export_gltf_with_materials
        
        # Use simple concrete material for visualization
        glb_bytes = export_gltf_with_materials(
            model["contours"],
            model["extrude_height"],
            wall_thickness=wall_thickness,
            material="concrete",
            binary=True,
            operations=model.get("metadata", {}).get("operations")
        )
        
        glb_storage_key, glb_size = storage_service.save_bytes(
            glb_bytes,
            role="output",
            job_id=job.id,
            filename="image_model.glb",
        )
        
        glb_file = FileModel(
            user_id=job.user_id,
            job_id=job.id,
            role="output",
            storage_key=glb_storage_key,
            original_name="image_model.glb",
            mime_type="model/gltf-binary",
            size_bytes=glb_size,
        )
        session.add(glb_file)
        await session.flush()
        logger.info("Generated visualization GLB for Image-to-2D job")
        
    except Exception as exc:
        logger.warning(f"Failed to generate visualization GLB: {exc}")

    job.output_file_id = dxf_file.id
    merged_params = job.params or {}
    
    # Critical: Persist artifact IDs so frontend can enable download buttons
    merged_params["dxf_file_id"] = dxf_file.id
    merged_params["step_file_id"] = step_file.id
    if glb_file:
         merged_params["glb_file_id"] = glb_file.id
    
    if ai_metadata:
        merged_params["ai_metadata"] = ai_metadata
        
    job.params = merged_params
    job.status = "completed"
    job.error_code = None
    job.error_message = None


async def _generate_model(path: Path, job: Job) -> dict:
    params = job.params or {}
    height = float(params.get("extrude_height", 3000))
    wall_thickness = float(params.get("wall_thickness", 200.0))

    # Validating/Defaulting height
    if height <= 0:
        height = 3000.0  # Default to standard floor height if 0 or invalid

    is_2d_mode = (job.mode == "image_to_2d")

    contours: list[list[list[float]]]
    if vision_service.enabled:
        try:
            logger.info("Calling vision API for vectorization", extra={"job_id": job.id})
            contours = await vision_service.vectorize(path)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Vision API failed, falling back to local contours", extra={"error": str(exc)})
            contours = _extract_contours(
                _load_image(path),
                canny_threshold1=float(params.get("canny_threshold1", 50)),
                canny_threshold2=float(params.get("canny_threshold2", 150)),
                blur_kernel=int(params.get("blur_kernel", 5)),
                min_contour_area=float(params.get("min_contour_area", 10)),
                simplify_epsilon=float(params.get("simplify_epsilon", 0.01)),
                enhance_preprocessing=bool(params.get("enhance_preprocessing", True)),
                use_hough_lines=bool(params.get("use_hough_lines", False)),
                snap_to_axis=bool(params.get("snap_to_axis", False)),
            )
    else:
        image = _load_image(path)
        contours = _extract_contours(
            image,
            canny_threshold1=float(params.get("canny_threshold1", 50)),
            canny_threshold2=float(params.get("canny_threshold2", 150)),
            blur_kernel=int(params.get("blur_kernel", 5)),
            min_contour_area=float(params.get("min_contour_area", 10)),
            simplify_epsilon=float(params.get("simplify_epsilon", 0.01)),
            enhance_preprocessing=bool(params.get("enhance_preprocessing", True)),
            use_hough_lines=bool(params.get("use_hough_lines", False)),
            snap_to_axis=bool(params.get("snap_to_axis", False)),
        )

    return {
        "job_id": job.id,
        "contours": contours,
        "extrude_height": height,
        "wall_thickness": wall_thickness,
        "only_2d": bool(params.get("only_2d", False)) or is_2d_mode,
        "metadata": {
            "source": Path(path).name,
            "contour_count": len(contours),
        },
    }


def _load_image(path: Path) -> np.ndarray:
    # Read as grayscale so edge detection is stable regardless of color input.
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise CADLiftError(ErrorCode.IMG_READ_ERROR, details=f"Failed to read image at {path}")
    return image


def _preprocess_image(image: np.ndarray, enhance_contrast: bool = True) -> np.ndarray:
    """
    Apply preprocessing to improve edge detection quality.

    Args:
        image: Grayscale input image
        enhance_contrast: Whether to apply CLAHE contrast enhancement

    Returns:
        Preprocessed image ready for edge detection
    """
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    # This enhances local contrast and makes edges more prominent
    if enhance_contrast:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        image = clahe.apply(image)

    # Denoise while preserving edges using bilateral filter
    # This reduces noise without blurring edges
    image = cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)

    return image


def _detect_hough_lines(
    edges: np.ndarray,
    *,
    hough_threshold: int = 100,
    min_line_length: int = 50,
    max_line_gap: int = 10,
) -> list[tuple[float, float, float, float]]:
    """
    Detect straight lines using Hough Line Transform.

    Args:
        edges: Binary edge image
        hough_threshold: Minimum votes to detect a line
        min_line_length: Minimum line length in pixels
        max_line_gap: Maximum gap between line segments

    Returns:
        List of lines as (x1, y1, x2, y2) tuples
    """
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=hough_threshold,
        minLineLength=min_line_length,
        maxLineGap=max_line_gap,
    )

    if lines is None:
        return []

    # Convert from [[x1,y1,x2,y2]] to [(x1,y1,x2,y2)]
    return [(float(line[0][0]), float(line[0][1]), float(line[0][2]), float(line[0][3])) for line in lines]


def _snap_to_axis(points: list[list[float]], angle_threshold: float = 5.0) -> list[list[float]]:
    """
    Snap near-horizontal/vertical lines to exact horizontal/vertical.

    Args:
        points: Polygon points
        angle_threshold: Maximum angle deviation (degrees) to snap

    Returns:
        Snapped polygon points
    """
    if len(points) < 2:
        return points

    snapped = [points[0][:]]  # Copy first point

    for i in range(1, len(points)):
        prev = snapped[-1]
        curr = points[i][:]

        dx = curr[0] - prev[0]
        dy = curr[1] - prev[1]
        length = (dx**2 + dy**2) ** 0.5

        if length < 1:  # Skip very short segments
            continue

        angle = np.degrees(np.arctan2(dy, dx))

        # Snap to horizontal (0┬░ or 180┬░)
        if abs(angle) < angle_threshold or abs(abs(angle) - 180) < angle_threshold:
            curr[1] = prev[1]  # Same Y coordinate

        # Snap to vertical (90┬░ or -90┬░)
        elif abs(abs(angle) - 90) < angle_threshold:
            curr[0] = prev[0]  # Same X coordinate

        snapped.append(curr)

    return snapped


def _extract_contours(
    image: np.ndarray,
    *,
    canny_threshold1: float,
    canny_threshold2: float,
    blur_kernel: int,
    min_contour_area: float,
    simplify_epsilon: float = 0.01,  # Douglas-Peucker epsilon (% of perimeter)
    enhance_preprocessing: bool = True,  # Apply advanced preprocessing
    use_hough_lines: bool = False,  # Use Hough line detection (Phase 2.2.3)
    snap_to_axis: bool = False,  # Snap near-parallel lines to axis (Phase 2.2.4)
) -> list[list[list[float]]]:
    """
    Extract contours from image using edge detection.

    Args:
        image: Grayscale input image
        canny_threshold1: Lower threshold for Canny edge detection
        canny_threshold2: Upper threshold for Canny edge detection
        blur_kernel: Gaussian blur kernel size
        min_contour_area: Minimum contour area to keep
        simplify_epsilon: Douglas-Peucker epsilon (as fraction of perimeter)
        enhance_preprocessing: Apply CLAHE and bilateral filtering
        use_hough_lines: Use Hough line detection for wall detection (Phase 2.2.3)
        snap_to_axis: Snap near-horizontal/vertical lines to axis-aligned (Phase 2.2.4)

    Returns:
        List of polygons (each polygon is list of [x,y] points)
    """
    # Apply enhanced preprocessing if enabled
    if enhance_preprocessing:
        image = _preprocess_image(image, enhance_contrast=True)

    # Ensure blur kernel is valid
    if blur_kernel < 1:
        blur_kernel = 1
    # Gaussian kernels must be odd.
    if blur_kernel % 2 == 0:
        blur_kernel += 1

    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(image, (blur_kernel, blur_kernel), 0)

    # Detect edges using Canny
    edges = cv2.Canny(blurred, threshold1=canny_threshold1, threshold2=canny_threshold2)

    # Apply morphological closing to connect nearby edges
    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    polygons: list[list[list[float]]] = []
    for contour in contours:
        # Filter by area
        area = cv2.contourArea(contour)
        if area < min_contour_area:
            continue

        # Simplify using Douglas-Peucker algorithm
        perimeter = cv2.arcLength(contour, True)
        epsilon = simplify_epsilon * perimeter
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Convert to point list
        points = [[float(pt[0][0]), float(pt[0][1])] for pt in approx]

        # Apply axis snapping if enabled (Phase 2.2.4)
        if snap_to_axis and len(points) >= 3:
            points = _snap_to_axis(points, angle_threshold=5.0)

        if len(points) >= 3:
            polygons.append(points)

    # If Hough line detection is enabled, log the detected lines
    # (full integration with contour merging deferred, but lines are detected)
    if use_hough_lines:
        hough_lines = _detect_hough_lines(
            edges,
            hough_threshold=int(100),
            min_line_length=int(50),
            max_line_gap=int(10),
        )
        logger.info(
            "Hough line detection",
            extra={"line_count": len(hough_lines), "enabled": use_hough_lines},
        )

    if not polygons:
        raise CADLiftError(ErrorCode.IMG_NO_CONTOURS, details="No shapes detected after edge detection and filtering")

    # Sort by perimeter (larger shapes first) for deterministic ordering
    polygons.sort(key=lambda pts: -sum(
        ((pts[i][0] - pts[(i+1)%len(pts)][0])**2 + (pts[i][1] - pts[(i+1)%len(pts)][1])**2)**0.5
        for i in range(len(pts))
    ))

    return polygons
