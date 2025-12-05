from __future__ import annotations

import json
import logging
import tempfile
from pathlib import Path

import ezdxf
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import File as FileModel
from app.models import Job
from app.services.storage import storage_service
from app.pipelines.geometry import build_artifacts, build_artifacts_multistory
from app.core.errors import CADLiftError, ErrorCode
from app.services.co2tools_adapter import get_co2tools_service, Co2ToolsError
from app.services.dwg_converter import get_dwg_converter_service, DwgConverterError


async def run(job: Job, session: AsyncSession) -> None:
    if not job.input_file_id:
        raise CADLiftError(ErrorCode.SYS_FILE_NOT_FOUND, details="Job has no input_file_id")

    input_file = await session.get(FileModel, job.input_file_id)
    if not input_file:
        raise CADLiftError(ErrorCode.SYS_FILE_NOT_FOUND, details=f"File {job.input_file_id} not found in database")

    input_path = storage_service.resolve_path(input_file.storage_key)
    logger = logging.getLogger("cadlift.pipeline.cad")
    
    # Auto-convert DWG to DXF if needed
    original_filename = input_file.original_name or ""
    if original_filename.lower().endswith(".dwg"):
        logger.info("DWG file detected, converting to DXF", extra={"input_filename": original_filename})
        dwg_converter = get_dwg_converter_service()
        
        if not dwg_converter.enabled:
            raise CADLiftError(
                ErrorCode.CAD_READ_ERROR, 
                details="DWG files require ODA File Converter which is not available"
            )
        
        try:
            dwg_bytes = input_path.read_bytes()
            dxf_bytes = dwg_converter.convert_dwg_to_dxf(dwg_bytes)
            
            # Save converted DXF to temp file for processing
            with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tmp:
                tmp.write(dxf_bytes)
                input_path = Path(tmp.name)
            
            logger.info("DWG converted to DXF successfully", extra={"size": len(dxf_bytes)})
        except DwgConverterError as exc:
            raise CADLiftError(ErrorCode.CAD_READ_ERROR, details=str(exc)) from exc
    
    model = _generate_model(input_path, job)
    logger.info("Processing CAD job", extra={"job_id": job.id, "input": str(input_path)})

    # Persist JSON model for introspection/metadata.
    json_storage_key, json_size = storage_service.save_bytes(
        json.dumps(model, indent=2).encode("utf-8"),
        role="output_metadata",
        job_id=job.id,
        filename="model.json",
    )
    json_file = FileModel(
        user_id=job.user_id,
        job_id=job.id,
        role="output_metadata",
        storage_key=json_storage_key,
        original_name="model.json",
        mime_type="application/json",
        size_bytes=json_size,
    )
    session.add(json_file)
    await session.flush()

    # Persist CAD-ready DXF as the primary output.
    # Get wall thickness from model (default: 200mm for architectural quality)
    params = job.params or {}
    wall_thickness = float(model.get("wall_thickness", 200.0))
    only_2d = bool(params.get("only_2d", False))

    # Phase 6.3: Use multi-story generation if multiple floors detected
    if model.get("is_multistory", False) and model.get("floors"):
        logger.info(f"Generating multi-story artifacts: {len(model['floors'])} floors")
        dxf_bytes, step_bytes = build_artifacts_multistory(
            model["floors"],
            wall_thickness=wall_thickness,
            openings=model.get("openings", []),
            only_2d=only_2d,
        )
    else:
        dxf_bytes, step_bytes = build_artifacts(
            model["polygons"],
            model["extrude_height"],
            wall_thickness=wall_thickness,
            openings=model.get("openings", []),  # Phase 6.2 - door & window support
            only_2d=only_2d,
        )
    dxf_storage_key, dxf_size = storage_service.save_bytes(
        dxf_bytes,
        role="output",
        job_id=job.id,
        filename="model.dxf",
    )
    dxf_file = FileModel(
        user_id=job.user_id,
        job_id=job.id,
        role="output",
        storage_key=dxf_storage_key,
        original_name="model.dxf",
        mime_type="application/dxf",
        size_bytes=dxf_size,
    )
    session.add(dxf_file)
    await session.flush()

    # STEP placeholder for downstream CAD tools.
    step_storage_key, step_size = storage_service.save_bytes(
        step_bytes,
        role="output_step",
        job_id=job.id,
        filename="model.step",
    )
    step_file = FileModel(
        user_id=job.user_id,
        job_id=job.id,
        role="output_step",
        storage_key=step_storage_key,
        original_name="model.step",
        mime_type="application/step",
        size_bytes=step_size,
    )
    session.add(step_file)
    await session.flush()

    merged_params = job.params or {}
    merged_params["step_file_id"] = step_file.id

    # Generate 3D mesh using co2tools (enabled by default for DXF→3D conversion)
    use_co2tools = bool(params.get("use_co2tools", True))  # Default: enabled
    if use_co2tools:
        co2 = get_co2tools_service()
        if co2.enabled:
            try:
                # Read original DXF bytes for co2tools processing
                original_dxf_bytes = input_path.read_bytes()
                
                # Generate GLB (primary 3D output for frontend viewer)
                glb_bytes = co2.dxf_bytes_to_glb(
                    original_dxf_bytes,
                    extrude_height=float(model.get("extrude_height", 3000.0)),
                    layer_cut=None,  # Auto-detect layer
                )
                glb_storage_key, glb_size = storage_service.save_bytes(
                    glb_bytes,
                    role="output",
                    job_id=job.id,
                    filename="model.glb",
                )
                glb_file = FileModel(
                    user_id=job.user_id,
                    job_id=job.id,
                    role="output",
                    storage_key=glb_storage_key,
                    original_name="model.glb",
                    mime_type="model/gltf-binary",
                    size_bytes=glb_size,
                )
                session.add(glb_file)
                await session.flush()
                merged_params["glb_file_id"] = glb_file.id
                
                # Also generate STL as secondary output
                stl_bytes = co2.dxf_bytes_to_stl(
                    original_dxf_bytes,
                    extrude_height=float(model.get("extrude_height", 3000.0)),
                    layer_cut=None,  # Auto-detect layer
                )
                stl_storage_key, stl_size = storage_service.save_bytes(
                    stl_bytes,
                    role="output",
                    job_id=job.id,
                    filename="model.stl",
                )
                stl_file = FileModel(
                    user_id=job.user_id,
                    job_id=job.id,
                    role="output",
                    storage_key=stl_storage_key,
                    original_name="model.stl",
                    mime_type="application/sla",
                    size_bytes=stl_size,
                )
                session.add(stl_file)
                await session.flush()
                merged_params["stl_file_id"] = stl_file.id
                
                # Set GLB as the primary output for 3D viewing
                job.output_file_id = glb_file.id
                logger.info(f"co2tools generated GLB ({glb_size} bytes) and STL ({stl_size} bytes)")
                
            except Co2ToolsError as exc:
                logger.warning("co2tools 3D generation failed, falling back to DXF output", extra={"error": str(exc)})
                # Fall back to DXF as output
                job.output_file_id = dxf_file.id
        else:
            logger.info("co2tools not available; using DXF as primary output")
            job.output_file_id = dxf_file.id
    else:
        job.output_file_id = dxf_file.id

    job.params = merged_params
    job.status = "completed"
    job.error_code = None
    job.error_message = None


def _extract_floor_level_from_layer(layer_name: str) -> int | None:
    """
    Extract floor level from layer name (Phase 6.3).

    Detects patterns like:
    - FLOOR-0, FLOOR-1, FLOOR-2
    - FLOOR_0, FLOOR_1, FLOOR_2
    - 0-FLOOR, 1-FLOOR, 2-FLOOR
    - LEVEL-0, LEVEL-1, etc.

    Args:
        layer_name: DXF layer name

    Returns:
        Floor level (int) or None if no floor level detected
    """
    import re

    if not layer_name:
        return None

    layer_upper = layer_name.upper()

    # Pattern 1: FLOOR-N or FLOOR_N
    match = re.search(r"FLOOR[-_](\d+)", layer_upper)
    if match:
        return int(match.group(1))

    # Pattern 2: N-FLOOR or N_FLOOR
    match = re.search(r"(\d+)[-_]FLOOR", layer_upper)
    if match:
        return int(match.group(1))

    # Pattern 3: LEVEL-N or LEVEL_N
    match = re.search(r"LEVEL[-_](\d+)", layer_upper)
    if match:
        return int(match.group(1))

    # Pattern 4: N-LEVEL or N_LEVEL
    match = re.search(r"(\d+)[-_]LEVEL", layer_upper)
    if match:
        return int(match.group(1))

    return None


def _generate_model(path: Path, job: Job) -> dict:
    try:
        doc = ezdxf.readfile(path)
    except ezdxf.DXFError as exc:
        raise CADLiftError(ErrorCode.CAD_INVALID_FORMAT, details=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise CADLiftError(ErrorCode.CAD_READ_ERROR, details=str(exc)) from exc

    msp = doc.modelspace()
    polygons: list[list[list[float]]] = []
    polygons_by_floor: dict[int, list[list[list[float]]]] = {}  # Phase 6.3

    params = job.params or {}
    max_polygons = int(params.get("max_polygons", 1000))

    # Layer filtering (if specified)
    allowed_layers = params.get("layers", None)  # None = all layers
    if allowed_layers and isinstance(allowed_layers, str):
        allowed_layers = [l.strip() for l in allowed_layers.split(",")]

    def _should_process_entity(entity) -> bool:
        """Check if entity should be processed based on layer filtering."""
        if allowed_layers is None:
            return True
        entity_layer = getattr(entity.dxf, "layer", "0")
        return entity_layer in allowed_layers

    def _add_polygon(points: list[list[float]], floor_level: int | None = None) -> None:
        """
        Add polygon to the appropriate floor (Phase 6.3).

        Accept clockwise and counter-clockwise windings; normalize to CCW so downstream
        offset/extrusion behaves consistently.
        """
        if len(points) < 3:
            return

        area = _polygon_area(points)
        if abs(area) <= 1e-6:
            return  # Degenerate polygon
        if area < 0:
            points = list(reversed(points))  # Normalize to CCW

        polygons.append(points)

        # Track floor (Phase 6.3)
        if floor_level is not None:
            if floor_level not in polygons_by_floor:
                polygons_by_floor[floor_level] = []
            polygons_by_floor[floor_level].append(points)

    # LWPOLYLINE
    for entity in msp.query("LWPOLYLINE"):
        if not _should_process_entity(entity):
            continue
        if not getattr(entity, "closed", False):
            continue
        pts = [[float(p[0]), float(p[1])] for p in entity.get_points()]
        # Detect floor level from layer (Phase 6.3)
        floor_level = _extract_floor_level_from_layer(getattr(entity.dxf, "layer", ""))
        _add_polygon(pts, floor_level)
        if len(polygons) >= max_polygons:
            break

    # POLYLINE
    if len(polygons) < max_polygons:
        for entity in msp.query("POLYLINE"):
            if not _should_process_entity(entity):
                continue
            if not entity.is_closed:
                continue
            pts = [[float(v.dxf.location.x), float(v.dxf.location.y)] for v in entity.vertices]
            # Detect floor level from layer (Phase 6.3)
            floor_level = _extract_floor_level_from_layer(getattr(entity.dxf, "layer", ""))
            _add_polygon(pts, floor_level)
            if len(polygons) >= max_polygons:
                break

    # CIRCLE (convert to polyline)
    if len(polygons) < max_polygons:
        import math
        num_segments = int(params.get("circle_segments", 36))  # Default: 10° per segment

        for entity in msp.query("CIRCLE"):
            if not _should_process_entity(entity):
                continue
            try:
                cx = float(entity.dxf.center.x)
                cy = float(entity.dxf.center.y)
                radius = float(entity.dxf.radius)

                # Generate circle as polygon
                pts = []
                for i in range(num_segments):
                    angle = 2 * math.pi * i / num_segments
                    x = cx + radius * math.cos(angle)
                    y = cy + radius * math.sin(angle)
                    pts.append([x, y])

                # Detect floor level from layer (Phase 6.3)
                floor_level = _extract_floor_level_from_layer(getattr(entity.dxf, "layer", ""))
                _add_polygon(pts, floor_level)
                if len(polygons) >= max_polygons:
                    break
            except Exception:
                continue

    # ARC (convert to polyline and close)
    if len(polygons) < max_polygons:
        import math

        for entity in msp.query("ARC"):
            if not _should_process_entity(entity):
                continue
            try:
                cx = float(entity.dxf.center.x)
                cy = float(entity.dxf.center.y)
                radius = float(entity.dxf.radius)
                start_angle = math.radians(float(entity.dxf.start_angle))
                end_angle = math.radians(float(entity.dxf.end_angle))

                # Normalize angles
                if end_angle < start_angle:
                    end_angle += 2 * math.pi

                arc_length = end_angle - start_angle
                num_segments = max(8, int(36 * arc_length / (2 * math.pi)))

                # Generate arc points
                pts = []
                for i in range(num_segments + 1):
                    angle = start_angle + (arc_length * i / num_segments)
                    x = cx + radius * math.cos(angle)
                    y = cy + radius * math.sin(angle)
                    pts.append([x, y])

                # Close arc to center to form a closed polygon (pie slice)
                pts.append([cx, cy])

                # Detect floor level from layer (Phase 6.3)
                floor_level = _extract_floor_level_from_layer(getattr(entity.dxf, "layer", ""))
                _add_polygon(pts, floor_level)
                if len(polygons) >= max_polygons:
                    break
            except Exception:
                continue

    # SPLINE (approximate)
    if len(polygons) < max_polygons:
        for entity in msp.query("SPLINE"):
            if not _should_process_entity(entity):
                continue
            try:
                pts = entity.approximate(40)  # coarse approximation
                pts_list = [[float(p[0]), float(p[1])] for p in pts]
                pts_list.append(pts_list[0])
                # Detect floor level from layer (Phase 6.3)
                floor_level = _extract_floor_level_from_layer(getattr(entity.dxf, "layer", ""))
                _add_polygon(pts_list, floor_level)
            except Exception:
                continue
            if len(polygons) >= max_polygons:
                break

    if not polygons:
        raise CADLiftError(ErrorCode.CAD_NO_CLOSED_SHAPES, details="No POLYLINE, CIRCLE, ARC, or SPLINE entities found")

    height = float(params.get("extrude_height", 3000))
    wall_thickness = float(params.get("wall_thickness", 200.0))

    # Extract TEXT entities (Phase 2.1.3 - room labels/dimensions)
    text_labels = _extract_text_labels(msp, polygons, allowed_layers)

    # Extract door/window openings (Phase 6.2 - door & window support)
    openings = _extract_openings(msp, polygons, allowed_layers, height)

    # Phase 6.3: Multi-story building support
    # If multiple floors detected from layer names, construct floor data
    is_multistory = len(polygons_by_floor) > 1
    floors = None

    if is_multistory:
        # Sort floors by level
        sorted_floor_levels = sorted(polygons_by_floor.keys())

        # Calculate Z-offsets (cumulative heights)
        z_offset = 0.0
        floors = []

        for floor_level in sorted_floor_levels:
            floor_polygons = polygons_by_floor[floor_level]
            floor_height = height  # Use same height for all floors (can be customized per floor)

            floors.append({
                "level": floor_level,
                "polygons": floor_polygons,
                "height": floor_height,
                "z_offset": z_offset
            })

            z_offset += floor_height

        logger = logging.getLogger("cadlift.pipeline.cad")
        logger.info(f"Detected multi-story building: {len(floors)} floors (levels {sorted_floor_levels})")

    return {
        "job_id": job.id,
        "polygons": polygons,
        "extrude_height": height,
        "wall_thickness": wall_thickness,
        "text_labels": text_labels,  # Phase 2.1.3
        "openings": openings,  # Phase 6.2
        "is_multistory": is_multistory,  # Phase 6.3
        "floors": floors,  # Phase 6.3
        "metadata": {
            "source": Path(path).name,
            "polygon_count": len(polygons),
            "text_label_count": len(text_labels),  # Phase 2.1.3
            "opening_count": len(openings),  # Phase 6.2
            "floor_count": len(floors) if floors else 1,  # Phase 6.3
        },
    }


def _extract_text_labels(msp, polygons: list[list[list[float]]], allowed_layers) -> list[dict]:
    """
    Extract TEXT and MTEXT entities from DXF (Phase 2.1.3).

    Associates text labels with nearby polygons (room labels).

    Args:
        msp: DXF modelspace
        polygons: List of extracted polygons
        allowed_layers: Layer filter (or None for all layers)

    Returns:
        List of text label dicts with {text, position, polygon_index}
    """
    logger = logging.getLogger("cadlift.pipeline.cad")
    text_labels = []

    def _should_process_text(entity) -> bool:
        """Check if text entity should be processed based on layer filtering."""
        if allowed_layers is None:
            return True
        entity_layer = getattr(entity.dxf, "layer", "0")
        return entity_layer in allowed_layers

    # Extract TEXT entities
    for entity in msp.query("TEXT"):
        if not _should_process_text(entity):
            continue
        try:
            text = entity.dxf.text.strip()
            if not text:
                continue

            position = [float(entity.dxf.insert.x), float(entity.dxf.insert.y)]

            # Find nearest polygon (assign text as potential room label)
            nearest_polygon_idx = _find_nearest_polygon(position, polygons)

            text_labels.append({
                "text": text,
                "position": position,
                "polygon_index": nearest_polygon_idx,
                "type": "TEXT",
            })
        except Exception as e:
            logger.warning(f"Failed to parse TEXT entity: {e}")
            continue

    # Extract MTEXT entities (multi-line text)
    for entity in msp.query("MTEXT"):
        if not _should_process_text(entity):
            continue
        try:
            text = entity.text.strip()
            if not text:
                continue

            position = [float(entity.dxf.insert.x), float(entity.dxf.insert.y)]

            nearest_polygon_idx = _find_nearest_polygon(position, polygons)

            text_labels.append({
                "text": text,
                "position": position,
                "polygon_index": nearest_polygon_idx,
                "type": "MTEXT",
            })
        except Exception as e:
            logger.warning(f"Failed to parse MTEXT entity: {e}")
            continue

    logger.info(f"Extracted {len(text_labels)} text labels from DXF")
    return text_labels


def _find_nearest_polygon(point: list[float], polygons: list[list[list[float]]]) -> int | None:
    """
    Find the nearest polygon to a given point (for associating text labels).

    Args:
        point: [x, y] coordinates
        polygons: List of polygons

    Returns:
        Index of nearest polygon, or None if no polygons
    """
    if not polygons:
        return None

    min_distance = float('inf')
    nearest_idx = 0

    for idx, polygon in enumerate(polygons):
        # Calculate distance to polygon centroid
        cx = sum(p[0] for p in polygon) / len(polygon)
        cy = sum(p[1] for p in polygon) / len(polygon)

        distance = ((point[0] - cx) ** 2 + (point[1] - cy) ** 2) ** 0.5

        if distance < min_distance:
            min_distance = distance
            nearest_idx = idx

    return nearest_idx


def _extract_openings(msp, polygons: list[list[list[float]]], allowed_layers, extrude_height: float) -> list[dict]:
    """
    Extract door and window openings from DXF (Phase 6.2).

    Detects openings from:
    - INSERT blocks with names containing "DOOR", "WINDOW"
    - Entities on layers named "DOORS", "WINDOWS", "OPENINGS"
    - Small closed polylines/rectangles (heuristic)

    Args:
        msp: DXF modelspace
        polygons: List of extracted wall polygons
        allowed_layers: Layer filter (or None for all layers)
        extrude_height: Building height (for default window/door heights)

    Returns:
        List of opening dicts with {type, position, width, height, polygon_index, wall_segment}
    """
    logger = logging.getLogger("cadlift.pipeline.cad")
    openings = []

    # Opening layer names to detect (case-insensitive)
    opening_layer_names = {"DOORS", "DOOR", "WINDOWS", "WINDOW", "OPENINGS", "OPENING"}

    def _should_process_opening(entity) -> bool:
        """Check if entity should be processed as an opening."""
        if allowed_layers is not None:
            entity_layer = getattr(entity.dxf, "layer", "0")
            if entity_layer not in allowed_layers:
                return False

        # Check if entity is on a known opening layer
        entity_layer = getattr(entity.dxf, "layer", "0").upper()
        return entity_layer in opening_layer_names

    # Strategy 1: Detect INSERT blocks (door/window symbols)
    for entity in msp.query("INSERT"):
        try:
            block_name = entity.dxf.name.upper()

            # Check if block name contains door/window keywords
            is_door = any(keyword in block_name for keyword in ["DOOR", "DR", "GATE"])
            is_window = any(keyword in block_name for keyword in ["WINDOW", "WIN", "WDW"])

            if not (is_door or is_window):
                continue

            # Get insertion point
            insert_point = entity.dxf.insert
            position = [float(insert_point.x), float(insert_point.y)]

            # Get rotation (in degrees)
            rotation = float(getattr(entity.dxf, "rotation", 0.0))

            # Try to get dimensions from block attributes or use defaults
            # Standard dimensions: Door = 900mm wide, Window = 1200mm wide
            width = 900.0 if is_door else 1200.0
            height = 2100.0 if is_door else 1200.0  # Door height 2.1m, window 1.2m

            # Determine which polygon and wall segment this opening belongs to
            polygon_idx, wall_segment = _find_nearest_wall_segment(position, polygons)

            if polygon_idx is None:
                logger.warning(f"Opening at {position} has no nearby wall, skipping")
                continue

            openings.append({
                "type": "door" if is_door else "window",
                "position": position,
                "width": width,
                "height": height,
                "rotation": rotation,
                "polygon_index": polygon_idx,
                "wall_segment": wall_segment,
                "z_offset": 0.0 if is_door else 1000.0,  # Windows at 1m height, doors at ground
                "source": "INSERT",
                "block_name": block_name,
            })

        except Exception as e:
            logger.warning(f"Failed to parse INSERT block as opening: {e}")
            continue

    # Strategy 2: Detect small rectangles on door/window layers
    for entity in msp.query("LWPOLYLINE"):
        if not _should_process_opening(entity):
            continue

        try:
            # Only process closed polylines
            if not getattr(entity, "closed", False):
                continue

            pts = [[float(p[0]), float(p[1])] for p in entity.get_points()]

            # Check if it's a rectangle (4 points)
            if len(pts) != 4:
                continue

            # Calculate bounding box to get dimensions
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            width = max(xs) - min(xs)
            height = max(ys) - min(ys)

            # Filter by size (openings are typically 0.5m - 3m wide/tall)
            if width < 500 or width > 3000 or height < 500 or height > 3000:
                continue

            # Calculate center position
            cx = sum(xs) / len(xs)
            cy = sum(ys) / len(ys)
            position = [cx, cy]

            # Determine type based on layer name and dimensions
            layer_name = entity.dxf.layer.upper()
            is_door = "DOOR" in layer_name or (width < 1500 and height > 1800)

            # Find nearest wall segment
            polygon_idx, wall_segment = _find_nearest_wall_segment(position, polygons)

            if polygon_idx is None:
                continue

            openings.append({
                "type": "door" if is_door else "window",
                "position": position,
                "width": width,
                "height": height,
                "rotation": 0.0,
                "polygon_index": polygon_idx,
                "wall_segment": wall_segment,
                "z_offset": 0.0 if is_door else 1000.0,
                "source": "POLYLINE",
                "layer": entity.dxf.layer,
            })

        except Exception as e:
            logger.warning(f"Failed to parse LWPOLYLINE as opening: {e}")
            continue

    logger.info(f"Extracted {len(openings)} openings from DXF ({sum(1 for o in openings if o['type'] == 'door')} doors, {sum(1 for o in openings if o['type'] == 'window')} windows)")
    return openings


def _find_nearest_wall_segment(point: list[float], polygons: list[list[list[float]]]) -> tuple[int | None, int | None]:
    """
    Find the nearest wall segment for an opening.

    Args:
        point: [x, y] coordinates of the opening
        polygons: List of wall polygons

    Returns:
        Tuple of (polygon_index, wall_segment_index), or (None, None) if no nearby wall
    """
    if not polygons:
        return None, None

    min_distance = float('inf')
    nearest_polygon_idx = None
    nearest_segment_idx = None

    for poly_idx, polygon in enumerate(polygons):
        # Check distance to each wall segment (edge)
        for seg_idx in range(len(polygon)):
            p1 = polygon[seg_idx]
            p2 = polygon[(seg_idx + 1) % len(polygon)]

            # Calculate distance from point to line segment
            distance = _point_to_segment_distance(point, p1, p2)

            if distance < min_distance:
                min_distance = distance
                nearest_polygon_idx = poly_idx
                nearest_segment_idx = seg_idx

    # Only accept if within reasonable distance (e.g., 500mm from wall)
    if min_distance > 500:
        return None, None

    return nearest_polygon_idx, nearest_segment_idx


def _point_to_segment_distance(point: list[float], seg_p1: list[float], seg_p2: list[float]) -> float:
    """
    Calculate minimum distance from a point to a line segment.

    Args:
        point: [x, y] point coordinates
        seg_p1: [x, y] segment start point
        seg_p2: [x, y] segment end point

    Returns:
        Distance in millimeters
    """
    px, py = point[0], point[1]
    x1, y1 = seg_p1[0], seg_p1[1]
    x2, y2 = seg_p2[0], seg_p2[1]

    # Vector from p1 to p2
    dx = x2 - x1
    dy = y2 - y1

    # Handle degenerate case (segment is a point)
    if dx == 0 and dy == 0:
        return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5

    # Parameter t represents position along segment (0 = p1, 1 = p2)
    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))

    # Closest point on segment
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy

    # Distance from point to closest point
    return ((px - closest_x) ** 2 + (py - closest_y) ** 2) ** 0.5


def _polygon_area(points: list[list[float]]) -> float:
    area = 0.0
    n = len(points)
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return area / 2.0
