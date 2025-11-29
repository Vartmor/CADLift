"""
Phase 4: Export Format Expansion - Test Suite

Tests for OBJ, STL, PLY, glTF, GLB mesh export functionality.
"""

from __future__ import annotations

import pytest

from app.pipelines.geometry import export_mesh, convert_cq_to_trimesh
from app.core.errors import CADLiftError, ErrorCode

# Test polygon: simple L-shaped room
L_SHAPED_POLYGON = [
    [
        [0, 0],
        [8000, 0],
        [8000, 5000],
        [3000, 5000],
        [3000, 3000],
        [0, 3000],
    ]
]


def test_export_obj_format():
    """Test OBJ export format."""
    result = export_mesh(
        polygons=L_SHAPED_POLYGON, height=3000, wall_thickness=200, format="obj", tolerance=0.1
    )

    assert isinstance(result, bytes)
    assert len(result) > 0

    # OBJ files are text-based, decode and check structure
    obj_text = result.decode("utf-8")
    assert "v " in obj_text  # Vertex lines
    assert "f " in obj_text  # Face lines
    assert obj_text.count("v ") > 10  # Should have many vertices


def test_export_stl_format():
    """Test STL binary export format."""
    result = export_mesh(
        polygons=L_SHAPED_POLYGON, height=3000, wall_thickness=200, format="stl", tolerance=0.1
    )

    assert isinstance(result, bytes)
    assert len(result) > 0

    # STL binary files have specific header structure
    assert len(result) > 84  # At least header (80) + triangle count (4)


def test_export_ply_format():
    """Test PLY export format."""
    result = export_mesh(
        polygons=L_SHAPED_POLYGON, height=3000, wall_thickness=200, format="ply", tolerance=0.1
    )

    assert isinstance(result, bytes)
    assert len(result) > 0


def test_export_glb_format():
    """Test GLB (glTF binary) export format."""
    result = export_mesh(
        polygons=L_SHAPED_POLYGON, height=3000, wall_thickness=200, format="glb", tolerance=0.1
    )

    assert isinstance(result, bytes)
    assert len(result) > 0

    # GLB files start with "glTF" magic header
    assert result[:4] == b"glTF"


def test_export_gltf_format():
    """Test glTF JSON export format."""
    result = export_mesh(
        polygons=L_SHAPED_POLYGON, height=3000, wall_thickness=200, format="gltf", tolerance=0.1
    )

    assert isinstance(result, bytes)
    assert len(result) > 0


def test_export_off_format():
    """Test OFF export format."""
    result = export_mesh(
        polygons=L_SHAPED_POLYGON, height=3000, wall_thickness=200, format="off", tolerance=0.1
    )

    assert isinstance(result, bytes)
    assert len(result) > 0

    # OFF files are text-based, check header
    off_text = result.decode("utf-8")
    assert off_text.startswith("OFF") or "OFF" in off_text[:10]


def test_export_unsupported_format():
    """Test that unsupported formats raise CADLiftError."""
    with pytest.raises(CADLiftError) as exc_info:
        export_mesh(
            polygons=L_SHAPED_POLYGON, height=3000, wall_thickness=200, format="fbx", tolerance=0.1
        )

    assert exc_info.value.error_code == ErrorCode.GEO_STEP_GENERATION_FAILED
    assert "Unsupported export format" in str(exc_info.value)


def test_export_with_solid_extrusion():
    """Test export with zero wall thickness (solid extrusion)."""
    result = export_mesh(
        polygons=L_SHAPED_POLYGON, height=3000, wall_thickness=0, format="obj", tolerance=0.1
    )

    assert isinstance(result, bytes)
    assert len(result) > 0


def test_export_with_thick_walls():
    """Test export with thick walls (500mm)."""
    result = export_mesh(
        polygons=L_SHAPED_POLYGON, height=3000, wall_thickness=500, format="stl", tolerance=0.1
    )

    assert isinstance(result, bytes)
    assert len(result) > 0


def test_export_multiple_polygons():
    """Test export with multiple separate polygons."""
    polygons = [
        [[0, 0], [3000, 0], [3000, 3000], [0, 3000]],  # Room 1
        [[5000, 0], [8000, 0], [8000, 3000], [5000, 3000]],  # Room 2
    ]

    result = export_mesh(polygons=polygons, height=3000, wall_thickness=200, format="obj", tolerance=0.1)

    assert isinstance(result, bytes)
    assert len(result) > 0


def test_export_different_tolerance():
    """Test export with different tessellation tolerances."""
    # Lower tolerance = more triangles, larger file
    result_low_tol = export_mesh(
        polygons=L_SHAPED_POLYGON, height=3000, wall_thickness=200, format="stl", tolerance=0.05
    )

    # Higher tolerance = fewer triangles, smaller file
    result_high_tol = export_mesh(
        polygons=L_SHAPED_POLYGON, height=3000, wall_thickness=200, format="stl", tolerance=0.5
    )

    assert isinstance(result_low_tol, bytes)
    assert isinstance(result_high_tol, bytes)
    # Lower tolerance should generally produce larger files (more detail)
    # (not always true for simple shapes, but a good heuristic)


def test_export_validation_no_polygons():
    """Test that empty polygon list raises CADLiftError."""
    with pytest.raises(CADLiftError) as exc_info:
        export_mesh(polygons=[], height=3000, wall_thickness=200, format="obj")

    assert exc_info.value.error_code == ErrorCode.GEO_NO_POLYGONS


def test_export_validation_invalid_height():
    """Test that invalid height raises CADLiftError."""
    with pytest.raises(CADLiftError) as exc_info:
        export_mesh(polygons=L_SHAPED_POLYGON, height=0, wall_thickness=200, format="obj")

    assert exc_info.value.error_code == ErrorCode.GEO_INVALID_HEIGHT


def test_export_validation_negative_wall_thickness():
    """Test that negative wall thickness raises CADLiftError."""
    with pytest.raises(CADLiftError) as exc_info:
        export_mesh(polygons=L_SHAPED_POLYGON, height=3000, wall_thickness=-100, format="obj")

    assert exc_info.value.error_code == ErrorCode.GEO_INVALID_WALL_THICKNESS


def test_export_format_case_insensitive():
    """Test that format parameter is case-insensitive."""
    result_lower = export_mesh(polygons=L_SHAPED_POLYGON, height=3000, wall_thickness=200, format="obj")
    result_upper = export_mesh(polygons=L_SHAPED_POLYGON, height=3000, wall_thickness=200, format="OBJ")
    result_mixed = export_mesh(polygons=L_SHAPED_POLYGON, height=3000, wall_thickness=200, format="Obj")

    assert isinstance(result_lower, bytes)
    assert isinstance(result_upper, bytes)
    assert isinstance(result_mixed, bytes)
    # All should produce similar results
    assert abs(len(result_lower) - len(result_upper)) < 100
    assert abs(len(result_lower) - len(result_mixed)) < 100


def test_export_small_room():
    """Test export with minimum realistic room size."""
    small_room = [[[0, 0], [1500, 0], [1500, 1500], [0, 1500]]]  # 1.5m x 1.5m

    result = export_mesh(polygons=small_room, height=2500, wall_thickness=100, format="obj")

    assert isinstance(result, bytes)
    assert len(result) > 0


def test_export_large_room():
    """Test export with large room size."""
    large_room = [[[0, 0], [20000, 0], [20000, 15000], [0, 15000]]]  # 20m x 15m

    result = export_mesh(polygons=large_room, height=4000, wall_thickness=300, format="stl")

    assert isinstance(result, bytes)
    assert len(result) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
