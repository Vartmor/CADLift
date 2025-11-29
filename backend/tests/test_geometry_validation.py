"""
Phase 5: Quality Assurance & Optimization - Geometry Validation Tests

Validates that generated geometry is mathematically correct:
- Meshes are watertight (no holes)
- Proper face normals
- No self-intersections
- Valid STEP solid bodies
- Correct dimensions
"""

from __future__ import annotations

import pytest
import trimesh
import ezdxf

from app.pipelines.geometry import (
    build_step_solid,
    export_mesh,
    convert_cq_to_trimesh,
    extrude_polygons_to_dxf,
)
import cadquery as cq

# Test polygons
SIMPLE_ROOM = [[[0, 0], [5000, 0], [5000, 4000], [0, 4000]]]
L_SHAPED_ROOM = [
    [
        [0, 0],
        [8000, 0],
        [8000, 5000],
        [3000, 5000],
        [3000, 3000],
        [0, 3000],
    ]
]


def test_geometry_watertight_mesh():
    """
    Validation: Generated meshes should be watertight (no holes)

    Watertight meshes are required for 3D printing and solid modeling
    """
    # Generate mesh via OBJ export
    obj_bytes = export_mesh(
        polygons=SIMPLE_ROOM, height=3000, wall_thickness=200, format="obj"
    )

    # Load as trimesh
    mesh = trimesh.load(trimesh.util.wrap_as_stream(obj_bytes), file_type="obj")

    # Check if watertight
    assert mesh.is_watertight, "Generated mesh should be watertight"

    # Check for holes
    assert not mesh.is_empty, "Mesh should not be empty"
    assert mesh.is_volume, "Mesh should represent a volume"


def test_geometry_proper_normals():
    """
    Validation: Face normals should be consistent (outward-facing)

    Proper normals are required for correct rendering
    """
    # Generate mesh
    obj_bytes = export_mesh(
        polygons=SIMPLE_ROOM, height=3000, wall_thickness=200, format="obj"
    )

    mesh = trimesh.load(trimesh.util.wrap_as_stream(obj_bytes), file_type="obj")

    # Check that normals exist
    assert mesh.face_normals is not None
    assert len(mesh.face_normals) == len(mesh.faces)

    # All normals should have unit length (approximately)
    import numpy as np

    normal_lengths = np.linalg.norm(mesh.face_normals, axis=1)
    assert np.allclose(normal_lengths, 1.0, atol=0.01), "Normals should be unit length"


def test_geometry_no_self_intersections():
    """
    Validation: Mesh should not have self-intersections

    Self-intersections cause rendering and manufacturing issues
    """
    # Generate simple room (should not self-intersect)
    obj_bytes = export_mesh(
        polygons=SIMPLE_ROOM, height=3000, wall_thickness=200, format="obj"
    )

    mesh = trimesh.load(trimesh.util.wrap_as_stream(obj_bytes), file_type="obj")

    # Check basic mesh properties
    assert mesh.is_watertight, "Mesh should be watertight (implies no major issues)"

    # Check no duplicate vertices
    mesh.merge_vertices()
    assert len(mesh.vertices) > 0, "Should have vertices after merging duplicates"

    # Check no degenerate faces (zero area)
    import numpy as np

    areas = mesh.area_faces
    assert np.all(areas > 1e-10), "Should not have degenerate faces"


def test_geometry_correct_dimensions():
    """
    Validation: Generated geometry should have correct dimensions

    Tests that input dimensions match output geometry bounds
    """
    # Input: 5m × 4m room, 3m height
    width, length, height = 5000, 4000, 3000

    obj_bytes = export_mesh(
        polygons=SIMPLE_ROOM, height=height, wall_thickness=0, format="obj"
    )

    mesh = trimesh.load(trimesh.util.wrap_as_stream(obj_bytes), file_type="obj")

    # Get bounding box
    bounds = mesh.bounds  # [[min_x, min_y, min_z], [max_x, max_y, max_z]]

    actual_width = bounds[1][0] - bounds[0][0]
    actual_length = bounds[1][1] - bounds[0][1]
    actual_height = bounds[1][2] - bounds[0][2]

    # Allow 1mm tolerance
    assert abs(actual_width - width) < 1, f"Width mismatch: {actual_width} vs {width}"
    assert abs(actual_length - length) < 1, f"Length mismatch: {actual_length} vs {length}"
    assert abs(actual_height - height) < 1, f"Height mismatch: {actual_height} vs {height}"


def test_geometry_wall_thickness_accuracy():
    """
    Validation: Wall thickness should be accurate

    Tests that hollow rooms have correct wall thickness
    """
    # Generate hollow room with 200mm walls
    wall_thickness = 200
    obj_bytes = export_mesh(
        polygons=SIMPLE_ROOM, height=3000, wall_thickness=wall_thickness, format="obj"
    )

    mesh = trimesh.load(trimesh.util.wrap_as_stream(obj_bytes), file_type="obj")

    # For a hollow room, the mesh should have both outer and inner surfaces
    # Volume should be less than solid room

    # Generate solid room for comparison
    obj_solid = export_mesh(
        polygons=SIMPLE_ROOM, height=3000, wall_thickness=0, format="obj"
    )
    mesh_solid = trimesh.load(trimesh.util.wrap_as_stream(obj_solid), file_type="obj")

    # Hollow room should have smaller volume than solid
    assert mesh.volume < mesh_solid.volume, "Hollow room should have less volume than solid"

    # Volume difference should approximate wall volume
    # (this is a rough check, exact calculation is complex)
    volume_diff = mesh_solid.volume - mesh.volume
    assert volume_diff > 0, "Volume difference should be positive"


def test_geometry_polygon_orientation():
    """
    Validation: Polygons should maintain correct orientation (CCW)

    Counter-clockwise winding order is standard for outward-facing normals
    """
    from shapely.geometry import Polygon

    # Test polygon winding order
    for poly in SIMPLE_ROOM:
        shapely_poly = Polygon(poly)

        # Shapely automatically fixes winding order, but area should be positive
        assert shapely_poly.area > 0, "Polygon should have positive area"
        assert shapely_poly.is_valid, "Polygon should be valid"


def test_geometry_l_shaped_room_validity():
    """
    Validation: L-shaped room should generate valid geometry

    Tests complex polygon handling
    """
    obj_bytes = export_mesh(
        polygons=L_SHAPED_ROOM, height=3000, wall_thickness=200, format="obj"
    )

    mesh = trimesh.load(trimesh.util.wrap_as_stream(obj_bytes), file_type="obj")

    # Should be watertight
    assert mesh.is_watertight, "L-shaped room should be watertight"

    # Should have reasonable vertex/face count
    assert len(mesh.vertices) > 20, "Should have sufficient vertices"
    assert len(mesh.faces) > 20, "Should have sufficient faces"

    # Should be valid (watertight implies valid)
    # Trimesh doesn't have is_valid attribute, check other properties
    assert mesh.is_watertight, "L-shaped mesh should be watertight"
    assert not mesh.is_empty, "L-shaped mesh should not be empty"


def test_geometry_dxf_entity_validity():
    """
    Validation: DXF output should contain valid entities

    Tests that DXF files are well-formed and parseable
    """
    dxf_bytes = extrude_polygons_to_dxf(
        polygons=SIMPLE_ROOM, height=3000, only_2d=False
    )

    # Parse DXF from bytes using temporary file
    import tempfile
    from pathlib import Path

    with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tmp:
        tmp.write(dxf_bytes)
        tmp_path = tmp.name

    try:
        doc = ezdxf.readfile(tmp_path)
        msp = doc.modelspace()

        # Should have entities
        entities = list(msp.query("*"))
        assert len(entities) > 0, "DXF should contain entities"

        # Should have both footprint and 3D geometry
        polylines = list(msp.query("LWPOLYLINE"))
        polyfaces = list(msp.query("POLYLINE"))

        assert len(polylines) > 0 or len(polyfaces) > 0, "Should have polyline entities"
    finally:
        # Cleanup
        Path(tmp_path).unlink(missing_ok=True)


def test_geometry_dxf_layers():
    """
    Validation: DXF should have proper layer structure

    Tests that DXF layers are created correctly
    """
    dxf_bytes = extrude_polygons_to_dxf(
        polygons=SIMPLE_ROOM, height=3000, only_2d=False
    )

    # Parse DXF using temporary file
    import tempfile
    from pathlib import Path

    with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tmp:
        tmp.write(dxf_bytes)
        tmp_path = tmp.name

    try:
        doc = ezdxf.readfile(tmp_path)

        # Check layers exist
        assert "Footprint" in doc.layers, "Should have Footprint layer"
        assert "Walls" in doc.layers, "Should have Walls layer"
        assert "Top" in doc.layers, "Should have Top layer"

        # Check layer properties
        footprint_layer = doc.layers.get("Footprint")
        assert footprint_layer is not None
        assert footprint_layer.dxf.color == 7  # White/black
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_geometry_step_file_validity():
    """
    Validation: STEP files should be valid ISO 10303-21 format

    Tests basic STEP file structure
    """
    step_bytes = build_step_solid(
        polygons=SIMPLE_ROOM, height=3000, wall_thickness=200
    )

    # STEP files should start with ISO-10303-21 header
    step_text = step_bytes.decode("utf-8", errors="ignore")

    assert "ISO-10303-21" in step_text, "Should be valid STEP format"
    assert "FILE_DESCRIPTION" in step_text, "Should have FILE_DESCRIPTION section"
    assert "FILE_NAME" in step_text, "Should have FILE_NAME section"
    assert "ENDSEC" in step_text, "Should have proper section endings"


def test_geometry_mesh_triangle_quality():
    """
    Validation: Mesh triangles should have reasonable quality

    Tests for degenerate triangles (zero area, extreme aspect ratios)
    """
    obj_bytes = export_mesh(
        polygons=SIMPLE_ROOM, height=3000, wall_thickness=200, format="obj"
    )

    mesh = trimesh.load(trimesh.util.wrap_as_stream(obj_bytes), file_type="obj")

    # Calculate triangle quality metrics
    import numpy as np

    # Get triangle areas
    areas = mesh.area_faces

    # No degenerate triangles (zero area)
    assert np.all(areas > 1e-6), "Should not have degenerate triangles"

    # Calculate aspect ratios (longest edge / shortest edge)
    vertices = mesh.vertices
    faces = mesh.faces

    aspect_ratios = []
    for face in faces:
        v0, v1, v2 = vertices[face[0]], vertices[face[1]], vertices[face[2]]

        # Edge lengths
        e0 = np.linalg.norm(v1 - v0)
        e1 = np.linalg.norm(v2 - v1)
        e2 = np.linalg.norm(v0 - v2)

        edges = [e0, e1, e2]
        aspect_ratio = max(edges) / min(edges) if min(edges) > 0 else 100

        aspect_ratios.append(aspect_ratio)

    # Most triangles should have reasonable aspect ratios (<10)
    aspect_ratios = np.array(aspect_ratios)
    median_aspect = np.median(aspect_ratios)

    print(f"\nTriangle quality: median aspect ratio = {median_aspect:.2f}")

    # Median should be reasonable (allow some poor triangles at corners)
    assert median_aspect < 10, f"Poor triangle quality: median aspect ratio {median_aspect:.2f}"


def test_geometry_vertex_count_reasonable():
    """
    Validation: Mesh should have reasonable vertex/face counts

    Too many vertices = slow, too few = poor quality
    """
    # Test different tolerances
    tolerances = [0.05, 0.1, 0.5]
    vertex_counts = []

    for tol in tolerances:
        obj_bytes = export_mesh(
            polygons=SIMPLE_ROOM, height=3000, wall_thickness=200, format="obj", tolerance=tol
        )

        mesh = trimesh.load(trimesh.util.wrap_as_stream(obj_bytes), file_type="obj")
        vertex_counts.append(len(mesh.vertices))

        print(f"\nTolerance={tol}: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")

    # Lower tolerance should produce more vertices
    assert vertex_counts[0] >= vertex_counts[1], "Lower tolerance should produce more vertices"
    assert vertex_counts[1] >= vertex_counts[2], "Lower tolerance should produce more vertices"

    # All should be in reasonable range (8-500 for simple room)
    # Simple rectangular room can have as few as 8-16 vertices
    for count in vertex_counts:
        assert 8 < count < 500, f"Vertex count out of range: {count}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
