"""
Test suite for complete Phase 2 features.

Tests all remaining Phase 2 items that were implemented:
- Phase 2.1.3: TEXT entity parsing
- Phase 2.2.3: Hough line detection
- Phase 2.2.4: Axis alignment
- Phase 2.2.5: 2D-only mode
- Phase 2.3.4: Multi-floor support
- Phase 2.3.5: Room relationships
- Phase 2.3.6: Dimension validation
"""

from pathlib import Path
import ezdxf
import numpy as np
import cv2
import pytest

from app.pipelines.cad import _generate_model, _extract_text_labels, _find_nearest_polygon
from app.pipelines.image import _extract_contours, _snap_to_axis, _detect_hough_lines
from app.pipelines.prompt import _instructions_to_model, _validate_room_dimensions, _detect_room_adjacency
from app.pipelines.geometry import extrude_polygons_to_dxf
from app.models import Job
from app.core.errors import CADLiftError


# Phase 2.1.3: TEXT Entity Parsing
def test_text_entity_extraction():
    """Test 2.1.3: Extract TEXT and MTEXT entities from DXF"""
    # Create DXF with text labels
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    # Add polygons (rooms)
    msp.add_lwpolyline([(0, 0), (5000, 0), (5000, 3000), (0, 3000)], close=True)
    msp.add_lwpolyline([(6000, 0), (10000, 0), (10000, 4000), (6000, 4000)], close=True)

    # Add TEXT labels
    msp.add_text("BEDROOM", dxfattribs={"insert": (2500, 1500), "height": 200})
    msp.add_text("KITCHEN", dxfattribs={"insert": (8000, 2000), "height": 200})

    # Add MTEXT
    msp.add_mtext("3.0m x 5.0m", dxfattribs={"insert": (2500, 500)})

    # Save and load (use a temp directory that exists on Windows)
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        path = str(Path(tmpdir) / "test_text_entities.dxf")
        doc.saveas(path)

        # Create mock job (use proper Job fields: job_type and mode)
        from pathlib import Path as PathlibPath
        job = Job(user_id="test-user", job_type="convert", mode="cad", params={})
        job.id = "test-job-1"

        # Generate model
        model = _generate_model(path, job)

        # Verify text labels extracted
        assert "text_labels" in model
        assert len(model["text_labels"]) == 3  # 2 TEXT + 1 MTEXT

    # Verify text content
    texts = [label["text"] for label in model["text_labels"]]
    assert "BEDROOM" in texts
    assert "KITCHEN" in texts
    assert "3.0m x 5.0m" in texts

    # Verify polygon association
    bedroom_label = [l for l in model["text_labels"] if l["text"] == "BEDROOM"][0]
    assert bedroom_label["polygon_index"] == 0  # First polygon

    kitchen_label = [l for l in model["text_labels"] if l["text"] == "KITCHEN"][0]
    assert kitchen_label["polygon_index"] == 1  # Second polygon

    print(f"✅ Test 2.1.3 passed: {len(model['text_labels'])} text labels extracted")
    return True


# Phase 2.2.3: Hough Line Detection
def test_hough_line_detection():
    """Test 2.2.3: Hough line detection for wall detection"""
    # Create test image with straight lines (walls)
    img = np.zeros((400, 400), dtype=np.uint8)

    # Draw horizontal and vertical lines (walls)
    cv2.line(img, (50, 50), (350, 50), 255, 2)    # Top wall
    cv2.line(img, (50, 350), (350, 350), 255, 2)  # Bottom wall
    cv2.line(img, (50, 50), (50, 350), 255, 2)    # Left wall
    cv2.line(img, (350, 50), (350, 350), 255, 2)  # Right wall

    # Detect edges
    edges = cv2.Canny(img, 50, 150)

    # Detect lines using Hough
    lines = _detect_hough_lines(edges, hough_threshold=50, min_line_length=100, max_line_gap=10)

    # Should detect 4 lines (one for each wall)
    assert len(lines) >= 4, f"Expected at least 4 lines, got {len(lines)}"

    # Verify lines are straight (endpoints have consistent x or y)
    for x1, y1, x2, y2 in lines:
        is_horizontal = abs(y1 - y2) < 10
        is_vertical = abs(x1 - x2) < 10
        assert is_horizontal or is_vertical, f"Line ({x1},{y1})->({x2},{y2}) is not axis-aligned"

    print(f"✅ Test 2.2.3 passed: {len(lines)} Hough lines detected")
    return True


# Phase 2.2.4: Axis Alignment
def test_axis_alignment():
    """Test 2.2.4: Snap near-parallel lines to axis"""
    # Create slightly tilted rectangle (simulating hand-drawn or noisy scan)
    polygon = [
        [0.0, 0.0],
        [100.0, 2.0],    # Almost horizontal (2° tilt)
        [102.0, 50.0],   # Almost vertical
        [2.0, 48.0],     # Almost vertical
    ]

    # Apply axis snapping
    snapped = _snap_to_axis(polygon, angle_threshold=5.0)

    # Verify snapping worked
    assert len(snapped) == len(polygon)

    # Check horizontal edges are snapped
    assert abs(snapped[0][1] - snapped[1][1]) < 0.01, "First edge should be horizontal"

    # Check vertical edges are snapped
    assert abs(snapped[1][0] - snapped[2][0]) < 0.01, "Second edge should be vertical"

    print(f"✅ Test 2.2.4 passed: Polygon snapped to axis-aligned edges")
    return True


def test_clockwise_polygons_supported():
    """Ensure clockwise DXF polygons are preserved and normalized"""
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    # Clockwise winding (negative shoelace area)
    cw_points = [(0, 0), (0, 3000), (4000, 3000), (4000, 0)]
    msp.add_lwpolyline(cw_points, close=True)

    import tempfile
    from pathlib import Path as PathlibPath

    with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tmp:
        doc.saveas(tmp.name)
        path = tmp.name

    job = Job(user_id="test-user", job_type="convert", mode="cad", params={})
    job.id = "clockwise-job"

    model = _generate_model(path, job)

    try:
        assert len(model["polygons"]) == 1, "Clockwise polygon should be retained"
        poly = model["polygons"][0]

        # Shoelace area should now be positive (CCW normalized)
        area = 0.0
        for i in range(len(poly)):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % len(poly)]
            area += x1 * y2 - x2 * y1
        area *= 0.5

        assert area > 0, "Polygon orientation should be normalized to CCW"
    finally:
        PathlibPath(path).unlink(missing_ok=True)

    print("✅ Clockwise polygons normalized and preserved")
    return True


# Phase 2.2.5: 2D-Only Mode
def test_2d_only_mode():
    """Test 2.2.5: 2D-only DXF export (no 3D geometry)"""
    polygons = [
        [[0, 0], [5000, 0], [5000, 3000], [0, 3000]],
    ]

    # Generate 3D DXF (default)
    dxf_3d = extrude_polygons_to_dxf(polygons, height=3000, only_2d=False)

    # Generate 2D-only DXF
    dxf_2d = extrude_polygons_to_dxf(polygons, height=3000, only_2d=True)

    # 2D DXF should be significantly smaller (no 3D mesh data)
    assert len(dxf_2d) < len(dxf_3d), "2D DXF should be smaller than 3D DXF"

    # Verify 2D DXF has footprint layer
    assert b"Footprint" in dxf_2d

    # Verify 2D DXF does NOT have wall mesh (fewer bytes)
    size_reduction_percent = (1 - len(dxf_2d) / len(dxf_3d)) * 100
    assert size_reduction_percent > 10, f"Expected >10% reduction, got {size_reduction_percent:.1f}%"

    print(f"✅ Test 2.2.5 passed: 2D-only mode reduces size by {size_reduction_percent:.1f}%")
    return True


# Phase 2.3.4: Multi-Floor Support
def test_multi_floor_support():
    """Test 2.3.4: Multi-floor building support"""
    instructions = {
        "rooms": [
            {"name": "ground_lobby", "width": 10000, "length": 5000, "floor": 0},
            {"name": "ground_office", "width": 6000, "length": 4000, "floor": 0},
            {"name": "first_conference", "width": 8000, "length": 6000, "floor": 1},
            {"name": "first_break", "width": 4000, "length": 3000, "floor": 1},
            {"name": "second_executive", "width": 12000, "length": 8000, "floor": 2},
        ]
    }

    model = _instructions_to_model(instructions, "multi-floor office building", {})

    # Verify metadata
    assert model["metadata"]["floor_count"] == 3  # Floors 0, 1, 2
    assert model["metadata"]["floors"] == [0, 1, 2]
    assert model["metadata"]["room_count"] == 5

    # Verify rooms_by_floor structure
    assert "rooms_by_floor" in model
    assert "0" in model["rooms_by_floor"]  # Ground floor
    assert "1" in model["rooms_by_floor"]  # First floor
    assert "2" in model["rooms_by_floor"]  # Second floor

    # Verify room counts per floor
    assert len(model["rooms_by_floor"]["0"]) == 2  # 2 ground floor rooms
    assert len(model["rooms_by_floor"]["1"]) == 2  # 2 first floor rooms
    assert len(model["rooms_by_floor"]["2"]) == 1  # 1 second floor room

    print(f"✅ Test 2.3.4 passed: {model['metadata']['floor_count']} floors with {model['metadata']['room_count']} rooms")
    return True


# Phase 2.3.5: Room Relationships
def test_room_adjacency_detection():
    """Test 2.3.5: Detect which rooms share walls"""
    instructions = {
        "rooms": [
            {"name": "bedroom1", "width": 4000, "length": 3000, "position": [0, 0]},
            {"name": "bedroom2", "width": 4000, "length": 3000, "position": [4000, 0]},  # Shares wall with bedroom1
            {"name": "bathroom", "width": 4000, "length": 3000, "position": [8000, 0]},  # Shares wall with bedroom2 (same height)
        ]
    }

    model = _instructions_to_model(instructions, "adjacent rooms", {})

    # Verify adjacencies detected
    assert "adjacencies" in model["metadata"]
    adjacencies = model["metadata"]["adjacencies"]

    # Should detect 2 adjacencies: bedroom1-bedroom2, bedroom2-bathroom
    assert len(adjacencies) >= 2, f"Expected at least 2 adjacencies, got {len(adjacencies)}"

    # Verify specific adjacencies
    room_pairs = [(adj["room1"], adj["room2"]) for adj in adjacencies]
    assert ("bedroom1", "bedroom2") in room_pairs or ("bedroom2", "bedroom1") in room_pairs
    assert ("bedroom2", "bathroom") in room_pairs or ("bathroom", "bedroom2") in room_pairs

    print(f"✅ Test 2.3.5 passed: {len(adjacencies)} adjacencies detected")
    return True


# Phase 2.3.6: Dimension Validation
def test_dimension_validation():
    """Test 2.3.6: Validate realistic room dimensions"""
    # Test 1: Too small (should fail)
    room_too_small = {"name": "closet", "width": 1000, "length": 1000}  # 1m x 1m - too small

    with pytest.raises(CADLiftError, match="too small"):
        _validate_room_dimensions(room_too_small, 0)

    # Test 2: Too large (should fail)
    room_too_large = {"name": "warehouse", "width": 100000, "length": 100000}  # 100m x 100m - too large

    with pytest.raises(CADLiftError, match="too large"):
        _validate_room_dimensions(room_too_large, 1)

    # Test 3: Valid dimensions (should pass)
    room_valid = {"name": "bedroom", "width": 4000, "length": 3000}  # 4m x 3m - realistic
    _validate_room_dimensions(room_valid, 2)  # Should not raise

    # Test 4: Integration test - dimensions validated in full pipeline
    instructions_invalid = {
        "rooms": [
            {"name": "tiny", "width": 500, "length": 500},  # Too small
        ]
    }

    with pytest.raises(CADLiftError, match="too small"):
        _instructions_to_model(instructions_invalid, "invalid dimensions", {})

    print(f"✅ Test 2.3.6 passed: Dimension validation working correctly")
    return True


# Run all tests
if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 2 COMPLETE - Full Feature Test Suite")
    print("=" * 60)

    tests = [
        ("2.1.3 TEXT Entity Parsing", test_text_entity_extraction),
        ("2.2.3 Hough Line Detection", test_hough_line_detection),
        ("2.2.4 Axis Alignment", test_axis_alignment),
        ("2.2.5 2D-Only Mode", test_2d_only_mode),
        ("2.3.4 Multi-Floor Support", test_multi_floor_support),
        ("2.3.5 Room Adjacency", test_room_adjacency_detection),
        ("2.3.6 Dimension Validation", test_dimension_validation),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            print(f"\n[TEST] {name}")
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {name} FAILED: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    if failed == 0:
        print("✅ ALL PHASE 2 FEATURES COMPLETE AND TESTED")
    else:
        print(f"❌ {failed} tests failed")
    print("=" * 60)
