from __future__ import annotations

"""
Geometry utilities for turning polygon footprints into CAD-friendly artifacts.

Uses cadquery (OpenCASCADE) for proper solid modeling and STEP export.
DXF generation remains lightweight with 3DFACE extrusions for compatibility.
"""

import io
import logging
import os
import tempfile
from typing import Iterable

import cadquery as cq
import ezdxf
import numpy as np
import trimesh
from ezdxf.render import MeshBuilder

from app.core.errors import CADLiftError, ErrorCode
from app.materials import (
    MATERIAL_LIBRARY,
    get_material_for_layer,
    generate_mtl_content,
    generate_gltf_materials
)

logger = logging.getLogger("cadlift.geometry")


def extrude_polygons_to_dxf_multistory(floors: list[dict], only_2d: bool = False) -> bytes:
    """
    Build a multi-story DXF with floor layers (Phase 6.3).

    Generates DXF with separate layers for each floor:
    - 2D footprint polylines on "FLOOR-{level}-Footprint" layers
    - 3D mesh walls and tops on "FLOOR-{level}-Walls" and "FLOOR-{level}-Top" layers

    Args:
        floors: List of floor dicts with structure:
            [
                {"level": 0, "polygons": [...], "height": 3000, "z_offset": 0},
                {"level": 1, "polygons": [...], "height": 3000, "z_offset": 3000}
            ]
        only_2d: If True, only generate 2D footprints (skip 3D geometry)

    Returns:
        bytes: Multi-story DXF file content with floor layers
    """
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    doc.units = ezdxf.units.MM

    for floor_idx, floor in enumerate(floors):
        level = floor.get("level", floor_idx)
        polygons = floor.get("polygons", [])
        height = floor.get("height", 3000.0)
        z_offset = floor.get("z_offset", 0.0)

        # Create layers for this floor
        footprint_layer = f"FLOOR-{level}-Footprint"
        walls_layer = f"FLOOR-{level}-Walls"
        top_layer = f"FLOOR-{level}-Top"

        doc.layers.add(footprint_layer, color=7 + level)
        doc.layers.add(walls_layer, color=8)
        doc.layers.add(top_layer, color=9)

        # Process each polygon
        for poly_idx, polygon in enumerate(polygons):
            if len(polygon) < 3:
                logger.warning(f"Skipping polygon {poly_idx} on floor {level}: insufficient points")
                continue

            # Add 2D footprint polyline
            msp.add_lwpolyline(
                polygon,
                close=True,
                dxfattribs={"layer": footprint_layer}
            )

            if only_2d:
                continue

            # Build 3D mesh for walls and top at floor Z offset
            mesh = MeshBuilder()

            bottom_vertices = [(p[0], p[1], z_offset) for p in polygon]
            top_vertices = [(p[0], p[1], z_offset + height) for p in polygon]

            n_points = len(polygon)

            # Add wall faces
            for i in range(n_points):
                next_i = (i + 1) % n_points
                mesh.add_face([
                    bottom_vertices[i],
                    bottom_vertices[next_i],
                    top_vertices[next_i],
                    top_vertices[i]
                ])

            # Add top face
            if n_points <= 4:
                mesh.add_face(top_vertices)
            else:
                # Fan triangulation
                cx = sum(p[0] for p in polygon) / n_points
                cy = sum(p[1] for p in polygon) / n_points
                center = (cx, cy, z_offset + height)

                for i in range(n_points):
                    next_i = (i + 1) % n_points
                    mesh.add_face([
                        top_vertices[i],
                        top_vertices[next_i],
                        center
                    ])

            mesh.render_polyface(msp, dxfattribs={"layer": walls_layer})

        logger.debug(f"Generated DXF for floor {level}: {len(polygons)} polygons, "
                    f"height={height}mm, z_offset={z_offset}mm")

    buffer = io.StringIO()
    doc.write(buffer)
    return buffer.getvalue().encode("utf-8")


def extrude_polygons_to_dxf(polygons: Iterable[list[list[float]]], height: float, only_2d: bool = False) -> bytes:
    """
    Build a DXF with improved 3D mesh structure using POLYFACE entities.

    Generates:
    - 2D footprint polylines on "Footprint" layer
    - 3D mesh walls and top surface on "Walls" and "Top" layers (unless only_2d=True)
    - Proper metadata (units in millimeters)

    Args:
        polygons: List of polygons, each polygon is a list of [x, y] coordinates
        height: Extrusion height in millimeters
        only_2d: If True, only generate 2D footprints (skip 3D geometry) [Phase 2.2.5]

    Returns:
        bytes: DXF file content with proper layer structure and mesh geometry
    """
    # Create DXF document with R2010 for better compatibility
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    # Set document units to millimeters
    doc.units = ezdxf.units.MM

    # Create layers with proper naming and colors
    doc.layers.add("Footprint", color=7)  # White/black
    doc.layers.add("Walls", color=8)      # Dark gray
    doc.layers.add("Top", color=9)        # Light gray

    # Process each polygon
    for poly_idx, polygon in enumerate(polygons):
        if len(polygon) < 3:
            logger.warning(f"Skipping polygon {poly_idx}: insufficient points ({len(polygon)})")
            continue

        # Add 2D footprint polyline on "Footprint" layer
        msp.add_lwpolyline(
            polygon,
            close=True,
            dxfattribs={"layer": "Footprint"}
        )

        # Skip 3D geometry if only_2d mode is enabled (Phase 2.2.5)
        if only_2d:
            continue

        # Build 3D mesh for walls and top
        mesh = MeshBuilder()

        # Create vertices: bottom loop at z=0, top loop at z=height
        bottom_vertices = [(p[0], p[1], 0.0) for p in polygon]
        top_vertices = [(p[0], p[1], height) for p in polygon]

        n_points = len(polygon)

        # Add wall faces (quadrilaterals connecting bottom to top)
        # Note: add_face() expects vertex coordinates, not indices
        for i in range(n_points):
            next_i = (i + 1) % n_points
            # Quad: bottom[i], bottom[next_i], top[next_i], top[i]
            mesh.add_face([
                bottom_vertices[i],
                bottom_vertices[next_i],
                top_vertices[next_i],
                top_vertices[i]
            ])

        # Add top face (polygon at height)
        # Note: For convex polygons, we can add the face directly
        # For concave polygons, this may not render correctly in POLYFACE
        if n_points <= 4:
            # Simple quad or triangle - add directly
            mesh.add_face(top_vertices)
        else:
            # Fan triangulation for n-gons (works better with POLYFACE)
            # Calculate center point
            cx = sum(p[0] for p in polygon) / n_points
            cy = sum(p[1] for p in polygon) / n_points
            center = (cx, cy, height)

            # Create triangular faces from center to each edge
            for i in range(n_points):
                next_i = (i + 1) % n_points
                mesh.add_face([
                    top_vertices[i],
                    top_vertices[next_i],
                    center
                ])

        # Render mesh as POLYFACE on "Walls" layer
        mesh.render_polyface(msp, dxfattribs={"layer": "Walls"})

    # Write to buffer
    buffer = io.StringIO()
    doc.write(buffer)
    return buffer.getvalue().encode("utf-8")


def _cut_openings_from_solid(solid: cq.Workplane, openings: list[dict], polygons: list[list[list[float]]], height: float, z_offset: float = 0.0) -> cq.Workplane:
    """
    Cut door/window openings from a solid using boolean subtraction (Phase 6.2 & 6.3).

    Args:
        solid: The wall solid to cut openings from
        openings: List of opening dicts with position, size, polygon_index, wall_segment
        polygons: List of wall polygons (for finding wall positions)
        height: Building height
        z_offset: Floor Z offset for multi-story buildings (Phase 6.3, default: 0)

    Returns:
        Modified solid with openings cut out
    """
    import math

    result = solid

    for idx, opening in enumerate(openings):
        try:
            # Get opening properties
            position = opening["position"]  # [x, y] in 2D
            width = opening["width"]
            opening_height = opening["height"]
            z_offset = opening.get("z_offset", 0.0)  # Height above ground (0 for doors, ~1000 for windows)
            polygon_idx = opening["polygon_index"]
            wall_segment_idx = opening["wall_segment"]

            # Get the wall segment this opening is on
            if polygon_idx is None or wall_segment_idx is None:
                logger.warning(f"Opening {idx} has no wall assignment, skipping")
                continue

            polygon = polygons[polygon_idx]
            p1 = polygon[wall_segment_idx]
            p2 = polygon[(wall_segment_idx + 1) % len(polygon)]

            # Calculate wall direction vector
            wall_dx = p2[0] - p1[0]
            wall_dy = p2[1] - p1[1]
            wall_length = (wall_dx ** 2 + wall_dy ** 2) ** 0.5

            if wall_length == 0:
                logger.warning(f"Opening {idx} on degenerate wall segment, skipping")
                continue

            # Normalize wall direction
            wall_dir_x = wall_dx / wall_length
            wall_dir_y = wall_dy / wall_length

            # Wall normal (perpendicular, pointing outward)
            wall_normal_x = -wall_dir_y
            wall_normal_y = wall_dir_x

            # Calculate opening center position in 3D
            # Project the opening position onto the wall segment
            # Find the closest point on the wall segment to the opening position
            t_param = ((position[0] - p1[0]) * wall_dir_x + (position[1] - p1[1]) * wall_dir_y)
            t_param = max(0, min(wall_length, t_param))  # Clamp to wall segment

            # Opening center on the wall (Phase 6.3: add floor z_offset for multi-story)
            opening_x = p1[0] + t_param * wall_dir_x
            opening_y = p1[1] + t_param * wall_dir_y
            opening_z = z_offset + opening.get("z_offset", 0.0) + opening_height / 2

            # Calculate rotation angle from wall direction
            angle = math.atan2(wall_dir_y, wall_dir_x)
            angle_degrees = math.degrees(angle)

            # Create opening box (slightly larger to ensure clean cut)
            # Box extends through the wall (depth = 1000mm to penetrate both sides)
            box_depth = 1000.0  # Penetrate through wall

            # Create box at origin, then rotate and translate
            opening_box = (
                cq.Workplane("XY")
                .box(width, box_depth, opening_height)
                .translate((opening_x, opening_y, opening_z))
                .rotate((opening_x, opening_y, 0), (opening_x, opening_y, 1), angle_degrees)
            )

            # Subtract opening from solid
            result = result.cut(opening_box)

            logger.debug(f"Cut opening {idx}: type={opening['type']}, "
                        f"position=({opening_x:.1f}, {opening_y:.1f}, {opening_z:.1f}), "
                        f"size={width}x{opening_height}mm")

        except Exception as e:
            logger.warning(f"Failed to cut opening {idx}: {e}")
            # Continue with other openings rather than failing completely
            continue

    return result


def build_step_solid_multistory(
    floors: list[dict],
    wall_thickness: float = 0.0,
    openings: list[dict] = None
) -> bytes:
    """
    Generate multi-story STEP solid with proper Z-stacking (Phase 6.3).

    Stacks floors vertically at different Z heights to create multi-story buildings.
    Each floor can have different height and polygons.

    Args:
        floors: List of floor dicts with structure:
            [
                {"level": 0, "polygons": [...], "height": 3000, "z_offset": 0},
                {"level": 1, "polygons": [...], "height": 3000, "z_offset": 3000},
                {"level": 2, "polygons": [...], "height": 3500, "z_offset": 6000}
            ]
        wall_thickness: Wall thickness in millimeters (default: 0 = solid)
        openings: List of door/window openings with floor_level specified

    Returns:
        bytes: Valid ISO 10303-21 STEP file content with stacked floors

    Raises:
        CADLiftError: If floor data is invalid or generation fails
    """
    if not floors:
        raise CADLiftError(ErrorCode.GEO_NO_POLYGONS, details="No floors provided for multi-story generation")

    if wall_thickness < 0:
        raise CADLiftError(ErrorCode.GEO_INVALID_WALL_THICKNESS, details=f"Invalid wall thickness: {wall_thickness}mm")

    if openings is None:
        openings = []

    try:
        # Helper function to create floor solid at specific Z height
        def create_floor_solid(
            polygons: list[list[list[float]]],
            height: float,
            z_offset: float,
            floor_openings: list[dict]
        ) -> cq.Workplane:
            """Create a single floor solid with vertical offset."""
            if not polygons:
                raise CADLiftError(ErrorCode.GEO_NO_POLYGONS, details="Floor has no polygons")

            # Helper to create single polygon solid
            def create_polygon_solid(poly: list[list[float]]) -> cq.Workplane:
                """Create solid or hollow extrusion from a polygon."""
                if len(poly) < 3:
                    raise CADLiftError(ErrorCode.GEO_INVALID_POLYGON, details=f"Polygon must have at least 3 points, got {len(poly)}")

                # Create outer solid at Z offset
                outer = (
                    cq.Workplane("XY")
                    .polyline([(p[0], p[1]) for p in poly])
                    .close()
                    .extrude(height)
                    .translate((0, 0, z_offset))
                )

                # If no wall thickness, return solid extrusion
                if wall_thickness <= 0:
                    return outer

                # Create hollow room by subtracting inner cavity
                try:
                    inner = (
                        cq.Workplane("XY")
                        .polyline([(p[0], p[1]) for p in poly])
                        .close()
                        .offset2D(-wall_thickness)
                        .extrude(height)
                        .translate((0, 0, z_offset))
                    )
                    return outer.cut(inner)
                except Exception as e:
                    logger.warning(f"Failed to create wall thickness: {e}, using solid")
                    return outer

            # Create union of all polygons for this floor
            result = create_polygon_solid(polygons[0])
            for idx, poly in enumerate(polygons[1:], start=1):
                if len(poly) < 3:
                    logger.warning(f"Skipping polygon {idx}: insufficient points")
                    continue
                try:
                    new_shape = create_polygon_solid(poly)
                    result = result.union(new_shape)
                except Exception as e:
                    logger.warning(f"Failed to add polygon {idx}: {e}")
                    continue

            # Cut openings for this floor
            if floor_openings:
                result = _cut_openings_from_solid(result, floor_openings, polygons, height, z_offset=z_offset)
                logger.debug(f"Cut {len(floor_openings)} openings from floor at Z={z_offset}")

            return result

        # Build each floor and union them
        result = None
        total_openings = 0

        for floor_idx, floor in enumerate(floors):
            level = floor.get("level", floor_idx)
            polygons = floor.get("polygons", [])
            height = floor.get("height", 3000.0)
            z_offset = floor.get("z_offset", 0.0)

            if height <= 0:
                raise CADLiftError(ErrorCode.GEO_INVALID_HEIGHT, details=f"Floor {level} has invalid height: {height}mm")

            # Filter openings for this floor
            floor_openings = [o for o in openings if o.get("floor_level", 0) == level]
            total_openings += len(floor_openings)

            # Create floor solid
            floor_solid = create_floor_solid(polygons, height, z_offset, floor_openings)

            logger.debug(f"Created floor {level}: {len(polygons)} polygons, "
                        f"height={height}mm, z_offset={z_offset}mm, openings={len(floor_openings)}")

            # Union with previous floors
            if result is None:
                result = floor_solid
            else:
                result = result.union(floor_solid)

        # Export to STEP format
        with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            cq.exporters.export(result, tmp_path, "STEP")

            with open(tmp_path, "rb") as f:
                step_bytes = f.read()

            logger.info(f"Generated multi-story STEP: {len(floors)} floors, "
                       f"wall_thickness={wall_thickness}mm, openings={total_openings}, "
                       f"size={len(step_bytes)} bytes")

            return step_bytes
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    except Exception as e:
        logger.error(f"Multi-story STEP generation failed: {e}")
        raise CADLiftError(ErrorCode.GEO_STEP_GENERATION_FAILED, details=f"Failed to generate multi-story STEP: {e}") from e


def build_step_solid(polygons: Iterable[list[list[float]]], height: float, wall_thickness: float = 0.0, openings: list[dict] = None) -> bytes:
    """
    Generate real STEP solid from polygons using cadquery/OpenCASCADE.

    Supports both solid extrusions and hollow rooms with wall thickness.
    Phase 6.2: Supports cutting door/window openings from walls.

    Args:
        polygons: List of polygons, each polygon is a list of [x, y] coordinates
        height: Extrusion height in millimeters
        wall_thickness: Wall thickness in millimeters (default: 0 = solid extrusion)
                       If > 0, creates hollow rooms by offsetting polygons inward
        openings: List of door/window openings to cut from walls (Phase 6.2)

    Returns:
        bytes: Valid ISO 10303-21 STEP file content

    Raises:
        ValueError: If polygons are invalid or empty
    """
    polygon_list = list(polygons)

    if not polygon_list:
        raise CADLiftError(ErrorCode.GEO_NO_POLYGONS, details="No polygons provided for STEP generation")

    if height <= 0:
        raise CADLiftError(ErrorCode.GEO_INVALID_HEIGHT, details=f"Invalid extrusion height: {height}mm. Must be positive.")

    if openings is None:
        openings = []

    if wall_thickness < 0:
        raise CADLiftError(ErrorCode.GEO_INVALID_WALL_THICKNESS, details=f"Invalid wall thickness: {wall_thickness}mm. Must be non-negative.")

    try:
        # Helper function to create a single polygon solid (with optional wall thickness)
        def create_polygon_solid(poly: list[list[float]]) -> cq.Workplane:
            """Create solid or hollow extrusion from a polygon."""
            if len(poly) < 3:
                raise CADLiftError(ErrorCode.GEO_INVALID_POLYGON, details=f"Polygon must have at least 3 points, got {len(poly)}")

            # Create outer solid
            outer = (
                cq.Workplane("XY")
                .polyline([(p[0], p[1]) for p in poly])
                .close()
                .extrude(height)
            )

            # If no wall thickness, return solid extrusion
            if wall_thickness <= 0:
                return outer

            # Create hollow room by subtracting inner cavity
            try:
                # Use offset2D to create inner polygon offset inward by wall_thickness
                inner = (
                    cq.Workplane("XY")
                    .polyline([(p[0], p[1]) for p in poly])
                    .close()
                    .offset2D(-wall_thickness)
                    .extrude(height)
                )

                # Subtract inner from outer to get walls
                return outer.cut(inner)

            except Exception as e:
                logger.warning(f"Failed to create wall thickness (offset2D failed): {e}")
                logger.warning(f"Falling back to solid extrusion")
                # Fallback: return solid extrusion if offset fails
                return outer

        # Start with the first polygon
        first_poly = polygon_list[0]
        result = create_polygon_solid(first_poly)

        if wall_thickness > 0:
            logger.debug(f"Created first polygon with {len(first_poly)} points, "
                        f"height={height}mm, wall_thickness={wall_thickness}mm")
        else:
            logger.debug(f"Created first polygon with {len(first_poly)} points, height={height}mm")

        # Add remaining polygons as unions
        for idx, poly in enumerate(polygon_list[1:], start=1):
            if len(poly) < 3:
                logger.warning(f"Skipping polygon {idx}: insufficient points ({len(poly)})")
                continue

            try:
                new_shape = create_polygon_solid(poly)
                result = result.union(new_shape)
                logger.debug(f"Added polygon {idx} with {len(poly)} points")
            except Exception as e:
                logger.warning(f"Failed to add polygon {idx}: {e}")
                # Continue with other polygons rather than failing completely
                continue

        # Phase 6.2: Cut door/window openings from walls
        if len(openings) > 0:
            result = _cut_openings_from_solid(result, openings, polygon_list, height)
            logger.info(f"Cut {len(openings)} openings from walls")

        # Export to STEP format
        # cadquery requires a file path, so we use a temporary file
        with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            # Export to temp file
            cq.exporters.export(result, tmp_path, "STEP")

            # Read back as bytes
            with open(tmp_path, "rb") as f:
                step_bytes = f.read()

            if len(openings) > 0:
                logger.info(f"Generated STEP solid: {len(polygon_list)} polygons, "
                           f"height={height}mm, wall_thickness={wall_thickness}mm, "
                           f"openings={len(openings)}, size={len(step_bytes)} bytes")
            elif wall_thickness > 0:
                logger.info(f"Generated STEP solid: {len(polygon_list)} polygons, "
                           f"height={height}mm, wall_thickness={wall_thickness}mm, "
                           f"size={len(step_bytes)} bytes")
            else:
                logger.info(f"Generated STEP solid: {len(polygon_list)} polygons, "
                           f"height={height}mm, size={len(step_bytes)} bytes")

            return step_bytes
        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except Exception:
                pass  # Ignore cleanup errors

    except Exception as e:
        logger.error(f"STEP generation failed: {e}")
        raise CADLiftError(ErrorCode.GEO_STEP_GENERATION_FAILED, details=f"Failed to generate STEP solid: {e}") from e


def build_artifacts_multistory(
    floors: list[dict],
    wall_thickness: float = 0.0,
    only_2d: bool = False,
    openings: list[dict] = None
) -> tuple[bytes, bytes]:
    """
    Generate both DXF and STEP artifacts for multi-story buildings (Phase 6.3).

    Args:
        floors: List of floor dicts with structure:
            [
                {"level": 0, "polygons": [...], "height": 3000, "z_offset": 0},
                {"level": 1, "polygons": [...], "height": 3000, "z_offset": 3000}
            ]
        wall_thickness: Wall thickness in millimeters (default: 0 = solid)
        only_2d: If True, generate only 2D footprints
        openings: List of door/window openings with floor_level specified

    Returns:
        tuple: (dxf_bytes, step_bytes) - Multi-story artifacts

    Raises:
        CADLiftError: If floors are invalid or generation fails
    """
    if not floors:
        raise CADLiftError(ErrorCode.GEO_NO_POLYGONS, details="No floors provided for multi-story generation")

    if wall_thickness < 0:
        raise CADLiftError(ErrorCode.GEO_INVALID_WALL_THICKNESS, details=f"Invalid wall thickness: {wall_thickness}mm")

    if openings is None:
        openings = []

    # Generate multi-story DXF
    dxf_bytes = extrude_polygons_to_dxf_multistory(floors, only_2d=only_2d)

    # Generate multi-story STEP (skip if 2D-only)
    if only_2d:
        step_bytes = b"/* 2D-only mode: STEP generation skipped */"
    else:
        step_bytes = build_step_solid_multistory(floors, wall_thickness, openings)

    logger.info(f"Generated multi-story artifacts: {len(floors)} floors, "
               f"DXF={len(dxf_bytes)} bytes, STEP={len(step_bytes)} bytes, "
               f"wall_thickness={wall_thickness}mm, openings={len(openings)}")

    return dxf_bytes, step_bytes


def build_artifacts(
    polygons: list[list[list[float]]],
    height: float,
    wall_thickness: float = 0.0,
    only_2d: bool = False,
    openings: list[dict] = None  # Phase 6.2 - door & window support
) -> tuple[bytes, bytes]:
    """
    Generate both DXF and STEP artifacts from polygons.

    Args:
        polygons: List of polygons, each polygon is a list of [x, y] coordinates
        height: Extrusion height in millimeters
        wall_thickness: Wall thickness in millimeters (default: 0 = solid extrusion)
                       If > 0, creates hollow rooms in STEP output
        only_2d: If True, generate only 2D footprints (Phase 2.2.5)
        openings: List of door/window openings to cut from walls (Phase 6.2)

    Returns:
        tuple: (dxf_bytes, step_bytes) - Both as ready-to-save byte arrays

    Raises:
        ValueError: If polygons are invalid or generation fails
    """
    if not polygons:
        raise CADLiftError(ErrorCode.GEO_NO_POLYGONS, details="No polygons provided for artifact generation")

    if height <= 0:
        raise CADLiftError(ErrorCode.GEO_INVALID_HEIGHT, details=f"Invalid height: {height}mm. Must be positive.")

    if wall_thickness < 0:
        raise CADLiftError(ErrorCode.GEO_INVALID_WALL_THICKNESS, details=f"Invalid wall thickness: {wall_thickness}mm. Must be non-negative.")

    if openings is None:
        openings = []

    # Generate DXF (lightweight POLYFACE mesh, or 2D-only)
    dxf_bytes = extrude_polygons_to_dxf(polygons, height, only_2d=only_2d)

    # Generate STEP (real solid model with optional wall thickness, skip if 2D-only)
    if only_2d:
        # For 2D-only mode, create minimal STEP placeholder
        step_bytes = b"/* 2D-only mode: STEP generation skipped */"
    else:
        step_bytes = build_step_solid(polygons, height, wall_thickness, openings)

    if len(openings) > 0:
        logger.info(f"Generated artifacts: DXF={len(dxf_bytes)} bytes, "
                   f"STEP={len(step_bytes)} bytes, wall_thickness={wall_thickness}mm, openings={len(openings)}")
    elif wall_thickness > 0:
        logger.info(f"Generated artifacts: DXF={len(dxf_bytes)} bytes, "
                   f"STEP={len(step_bytes)} bytes, wall_thickness={wall_thickness}mm")
    else:
        logger.info(f"Generated artifacts: DXF={len(dxf_bytes)} bytes, STEP={len(step_bytes)} bytes")

    return dxf_bytes, step_bytes


def convert_cq_to_trimesh(cq_shape: cq.Workplane, tolerance: float = 0.1) -> trimesh.Trimesh:
    """
    Convert a CadQuery shape to a trimesh object.

    Phase 4: Export Format Expansion
    Converts cadquery solid to triangulated mesh for export to OBJ, STL, glTF, etc.

    Args:
        cq_shape: CadQuery Workplane object containing the solid
        tolerance: Tessellation tolerance (smaller = more triangles)

    Returns:
        trimesh.Trimesh: Triangulated mesh object

    Raises:
        CADLiftError: If conversion fails
    """
    try:
        # Get the shape from the workplane
        shape = cq_shape.val()

        # Tessellate the shape to get vertices and triangles
        vertices, triangles = shape.tessellate(tolerance)

        # Convert cadquery vectors to numpy arrays
        vertices_np = np.array([[v.x, v.y, v.z] for v in vertices])
        triangles_np = np.array(triangles)

        # Create trimesh object (automatically merges duplicate vertices)
        mesh = trimesh.Trimesh(vertices=vertices_np, faces=triangles_np)

        logger.debug(f"Converted CadQuery shape to trimesh: {len(mesh.vertices)} vertices, "
                    f"{len(mesh.faces)} faces, watertight={mesh.is_watertight}")

        return mesh

    except Exception as e:
        logger.error(f"Failed to convert CadQuery shape to trimesh: {e}")
        raise CADLiftError(
            ErrorCode.GEO_STEP_GENERATION_FAILED,
            details=f"Failed to convert shape to mesh: {e}"
        ) from e


def export_mesh(
    polygons: list[list[list[float]]],
    height: float,
    wall_thickness: float = 0.0,
    format: str = "obj",
    tolerance: float = 0.1
) -> bytes:
    """
    Export polygons as a mesh file in various formats.

    Phase 4: Export Format Expansion
    Supports: OBJ, STL, PLY, OFF, glTF, GLB

    Args:
        polygons: List of polygons, each polygon is a list of [x, y] coordinates
        height: Extrusion height in millimeters
        wall_thickness: Wall thickness in millimeters (default: 0 = solid)
        format: Export format (obj, stl, ply, off, gltf, glb)
        tolerance: Tessellation tolerance (smaller = more triangles, default: 0.1)

    Returns:
        bytes: Mesh file content in the requested format

    Raises:
        CADLiftError: If export fails or format is unsupported
    """
    if not polygons:
        raise CADLiftError(ErrorCode.GEO_NO_POLYGONS, details="No polygons provided for mesh export")

    if height <= 0:
        raise CADLiftError(ErrorCode.GEO_INVALID_HEIGHT, details=f"Invalid height: {height}mm")

    if wall_thickness < 0:
        raise CADLiftError(ErrorCode.GEO_INVALID_WALL_THICKNESS, details=f"Invalid wall thickness: {wall_thickness}mm")

    # Supported formats
    supported_formats = ["obj", "stl", "ply", "off", "gltf", "glb"]
    format_lower = format.lower()

    if format_lower not in supported_formats:
        raise CADLiftError(
            ErrorCode.GEO_STEP_GENERATION_FAILED,
            details=f"Unsupported export format: {format}. Supported: {', '.join(supported_formats)}"
        )

    try:
        # Build the cadquery solid (reuse existing function)
        polygon_list = list(polygons)

        # Helper function to create a single polygon solid (copied from build_step_solid)
        def create_polygon_solid(poly: list[list[float]]) -> cq.Workplane:
            """Create solid or hollow extrusion from a polygon."""
            if len(poly) < 3:
                raise CADLiftError(ErrorCode.GEO_INVALID_POLYGON, details=f"Polygon must have at least 3 points, got {len(poly)}")

            # Create outer solid
            outer = (
                cq.Workplane("XY")
                .polyline([(p[0], p[1]) for p in poly])
                .close()
                .extrude(height)
            )

            # If no wall thickness, return solid extrusion
            if wall_thickness <= 0:
                return outer

            # Create hollow room by subtracting inner cavity
            try:
                inner = (
                    cq.Workplane("XY")
                    .polyline([(p[0], p[1]) for p in poly])
                    .close()
                    .offset2D(-wall_thickness)
                    .extrude(height)
                )
                return outer.cut(inner)
            except Exception as e:
                logger.warning(f"Failed to create wall thickness: {e}, using solid")
                return outer

        # Start with the first polygon
        result = create_polygon_solid(polygon_list[0])

        # Add remaining polygons as unions
        for idx, poly in enumerate(polygon_list[1:], start=1):
            if len(poly) < 3:
                logger.warning(f"Skipping polygon {idx}: insufficient points")
                continue
            try:
                new_shape = create_polygon_solid(poly)
                result = result.union(new_shape)
            except Exception as e:
                logger.warning(f"Failed to add polygon {idx}: {e}")
                continue

        # Convert to trimesh
        mesh = convert_cq_to_trimesh(result, tolerance=tolerance)

        # Export to requested format
        exported = mesh.export(file_type=format_lower)

        # Handle different return types
        if isinstance(exported, str):
            # Text-based formats (OBJ, OFF) return strings
            mesh_bytes = exported.encode('utf-8')
        elif isinstance(exported, dict):
            # glTF format returns a dict with multiple files
            # For glTF, combine all parts into a single JSON file
            if 'model.gltf' in exported:
                # Return the main glTF JSON file
                mesh_bytes = exported['model.gltf']
            else:
                # If no model.gltf, this shouldn't happen but handle gracefully
                import json
                mesh_bytes = json.dumps(exported).encode('utf-8')
        else:
            # Binary formats (STL, PLY, GLB) return bytes
            mesh_bytes = exported

        logger.info(f"Exported {format_lower.upper()}: {len(mesh.vertices)} vertices, "
                   f"{len(mesh.faces)} faces, size={len(mesh_bytes)} bytes")

        return mesh_bytes

    except CADLiftError:
        raise
    except Exception as e:
        logger.error(f"Mesh export failed ({format}): {e}")
        raise CADLiftError(
            ErrorCode.GEO_STEP_GENERATION_FAILED,
            details=f"Failed to export mesh as {format}: {e}"
        ) from e


def export_obj_with_mtl(
    polygons: list[list[list[float]]],
    height: float,
    wall_thickness: float = 0.0,
    material: str = "concrete",
    tolerance: float = 0.1
) -> tuple[bytes, bytes]:
    """
    Export polygons as OBJ file with MTL material file (Phase 6.4).

    Args:
        polygons: List of polygons, each polygon is a list of [x, y] coordinates
        height: Extrusion height in millimeters
        wall_thickness: Wall thickness in millimeters (default: 0 = solid)
        material: Material name from MATERIAL_LIBRARY
        tolerance: Tessellation tolerance

    Returns:
        tuple: (obj_bytes, mtl_bytes) - OBJ file and MTL file content
    """
    if not polygons:
        raise CADLiftError(ErrorCode.GEO_NO_POLYGONS, details="No polygons provided for OBJ export")

    # Generate the mesh (using existing function)
    obj_bytes = export_mesh(polygons, height, wall_thickness, format="obj", tolerance=tolerance)

    # Parse OBJ to add material reference
    obj_lines = obj_bytes.decode('utf-8').split('\n')
    obj_with_material = []

    obj_with_material.append("# CADLift OBJ Export with Materials (Phase 6.4)")
    obj_with_material.append(f"mtllib model.mtl")
    obj_with_material.append("")

    # Add all geometry
    for line in obj_lines:
        if line.startswith('#'):
            continue  # Skip existing comments
        obj_with_material.append(line)

    # Add material usage before faces
    obj_final = []
    material_added = False
    for line in obj_with_material:
        if line.startswith('f ') and not material_added:
            obj_final.append(f"usemtl {material}")
            obj_final.append("")
            material_added = True
        obj_final.append(line)

    obj_bytes_final = '\n'.join(obj_final).encode('utf-8')

    # Generate MTL file
    mtl_content = generate_mtl_content({material})
    mtl_bytes = mtl_content.encode('utf-8')

    logger.info(f"Exported OBJ+MTL with material '{material}': OBJ={len(obj_bytes_final)} bytes, MTL={len(mtl_bytes)} bytes")

    return obj_bytes_final, mtl_bytes


def export_gltf_with_materials(
    polygons: list[list[list[float]]],
    height: float,
    wall_thickness: float = 0.0,
    material: str = "concrete",
    tolerance: float = 0.1,
    binary: bool = False
) -> bytes:
    """
    Export polygons as glTF/GLB file with PBR materials (Phase 6.4).

    Args:
        polygons: List of polygons, each polygon is a list of [x, y] coordinates
        height: Extrusion height in millimeters
        wall_thickness: Wall thickness in millimeters (default: 0 = solid)
        material: Material name from MATERIAL_LIBRARY
        tolerance: Tessellation tolerance
        binary: If True, export as GLB (binary), otherwise glTF (JSON)

    Returns:
        bytes: glTF JSON or GLB binary content
    """
    import json

    if not polygons:
        raise CADLiftError(ErrorCode.GEO_NO_POLYGONS, details="No polygons provided for glTF export")

    # Generate the mesh
    polygon_list = list(polygons)

    # Helper function to create solid (copied from export_mesh)
    def create_polygon_solid(poly: list[list[float]]) -> cq.Workplane:
        if len(poly) < 3:
            raise CADLiftError(ErrorCode.GEO_INVALID_POLYGON, details=f"Polygon must have at least 3 points")

        outer = (
            cq.Workplane("XY")
            .polyline([(p[0], p[1]) for p in poly])
            .close()
            .extrude(height)
        )

        if wall_thickness <= 0:
            return outer

        try:
            inner = (
                cq.Workplane("XY")
                .polyline([(p[0], p[1]) for p in poly])
                .close()
                .offset2D(-wall_thickness)
                .extrude(height)
            )
            return outer.cut(inner)
        except Exception:
            return outer

    # Build solid
    result = create_polygon_solid(polygon_list[0])
    for idx, poly in enumerate(polygon_list[1:], start=1):
        if len(poly) >= 3:
            try:
                new_shape = create_polygon_solid(poly)
                result = result.union(new_shape)
            except Exception:
                continue

    # Convert to trimesh
    mesh = convert_cq_to_trimesh(result, tolerance=tolerance)

    # Generate glTF materials
    gltf_materials = generate_gltf_materials({material})

    # Export as glTF/GLB with materials
    # trimesh doesn't support material assignment directly, so we'll add it post-export
    if binary:
        # GLB export
        gltf_bytes = mesh.export(file_type='glb')

        logger.info(f"Exported GLB with material '{material}': {len(gltf_bytes)} bytes")
        return gltf_bytes
    else:
        # glTF JSON export
        gltf_dict = mesh.export(file_type='gltf')

        # Parse glTF JSON if it's a dict
        if isinstance(gltf_dict, dict):
            # Add materials to glTF
            if 'model.gltf' in gltf_dict:
                gltf_json = json.loads(gltf_dict['model.gltf'])
            else:
                gltf_json = gltf_dict
        else:
            gltf_json = json.loads(gltf_dict)

        # Add materials
        if 'materials' not in gltf_json:
            gltf_json['materials'] = []

        gltf_json['materials'].extend(gltf_materials)

        # Assign material to primitives
        if 'meshes' in gltf_json:
            for mesh_def in gltf_json['meshes']:
                for primitive in mesh_def.get('primitives', []):
                    primitive['material'] = 0  # Use first material

        gltf_bytes = json.dumps(gltf_json, indent=2).encode('utf-8')

        logger.info(f"Exported glTF with material '{material}': {len(gltf_bytes)} bytes")
        return gltf_bytes
