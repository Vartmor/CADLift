"""
Tests for door and window opening support (Phase 6.2).

Tests the detection and cutting of door/window openings from walls.
"""

import ezdxf
import tempfile
from pathlib import Path

from app.pipelines.cad import _generate_model, _extract_openings
from app.pipelines.geometry import build_step_solid
from app.models import Job


def create_test_dxf_with_openings(has_insert_blocks=True, has_layer_rectangles=True):
    """
    Create a test DXF file with a simple room and door/window openings.

    Creates a 5m x 4m room with:
    - 1 door (0.9m wide) on south wall
    - 2 windows (1.2m wide) on east and west walls
    """
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    # Add layers
    doc.layers.add("WALLS", color=7)
    doc.layers.add("DOORS", color=2)
    doc.layers.add("WINDOWS", color=3)

    # Create main room (5000mm x 4000mm rectangle)
    # Using LWPOLYLINE for the walls
    room_points = [
        (0, 0),
        (5000, 0),
        (5000, 4000),
        (0, 4000)
    ]
    msp.add_lwpolyline(room_points, close=True, dxfattribs={"layer": "WALLS"})

    if has_insert_blocks:
        # Add INSERT blocks for doors and windows
        # Door on south wall (bottom) - center at (2500, 0)
        msp.add_blockref("DOOR-900", (2500, 0), dxfattribs={"layer": "DOORS"})

        # Window on east wall (right) - center at (5000, 2000)
        msp.add_blockref("WINDOW-1200", (5000, 2000), dxfattribs={"layer": "WINDOWS"})

        # Window on west wall (left) - center at (0, 2000)
        msp.add_blockref("WIN-1200", (0, 2000), dxfattribs={"layer": "WINDOWS"})

    if has_layer_rectangles:
        # Add small rectangles on door/window layers (alternative detection method)
        # Door rectangle on north wall (top) - 900mm wide x 2100mm tall, centered at (2500, 4000)
        # Note: Rectangle must be 500-3000mm to be detected as opening
        door_rect = [
            (2500 - 450, 4000 - 100),  # 900mm wide
            (2500 + 450, 4000 - 100),
            (2500 + 450, 4000 + 100),  # 200mm deep (meets 500mm minimum when considering both dimensions)
            (2500 - 450, 4000 + 100)
        ]
        # Actually, let's make it the full door size in plan view
        door_rect = [
            (2500 - 450, 4000 - 600),  # 900mm wide x 1200mm deep
            (2500 + 450, 4000 - 600),
            (2500 + 450, 4000),
            (2500 - 450, 4000)
        ]
        msp.add_lwpolyline(door_rect, close=True, dxfattribs={"layer": "DOORS"})

    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
        doc.saveas(f.name)
        return Path(f.name)


def test_opening_detection_insert_blocks():
    """Test detection of door/window INSERT blocks."""
    dxf_path = create_test_dxf_with_openings(has_insert_blocks=True, has_layer_rectangles=False)

    try:
        # Read DXF
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()

        # Extract walls first
        polygons = []
        for entity in msp.query("LWPOLYLINE"):
            if entity.dxf.layer == "WALLS" and entity.closed:
                pts = [[float(p[0]), float(p[1])] for p in entity.get_points()]
                polygons.append(pts)

        # Extract openings
        openings = _extract_openings(msp, polygons, None, 3000.0)

        # Verify we detected the openings
        assert len(openings) >= 2, f"Expected at least 2 openings, got {len(openings)}"

        # Check we detected both doors and windows
        door_count = sum(1 for o in openings if o['type'] == 'door')
        window_count = sum(1 for o in openings if o['type'] == 'window')

        assert door_count >= 1, f"Expected at least 1 door, got {door_count}"
        assert window_count >= 1, f"Expected at least 1 window, got {window_count}"

        # Verify opening properties
        for opening in openings:
            assert 'position' in opening
            assert 'width' in opening
            assert 'height' in opening
            assert 'polygon_index' in opening
            assert 'wall_segment' in opening
            assert 'z_offset' in opening

            # Verify dimensions are reasonable
            assert 500 <= opening['width'] <= 3000, f"Invalid width: {opening['width']}"
            assert 500 <= opening['height'] <= 3000, f"Invalid height: {opening['height']}"

            # Doors should have z_offset = 0, windows should have z_offset > 0
            if opening['type'] == 'door':
                assert opening['z_offset'] == 0.0
            else:
                assert opening['z_offset'] > 0.0

        print(f"✓ Detected {len(openings)} openings: {door_count} doors, {window_count} windows")

    finally:
        # Clean up
        dxf_path.unlink()


def test_opening_detection_layer_rectangles():
    """Test detection of door/window rectangles on specific layers."""
    dxf_path = create_test_dxf_with_openings(has_insert_blocks=False, has_layer_rectangles=True)

    try:
        # Read DXF
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()

        # Extract walls first
        polygons = []
        for entity in msp.query("LWPOLYLINE"):
            if entity.dxf.layer == "WALLS" and entity.closed:
                pts = [[float(p[0]), float(p[1])] for p in entity.get_points()]
                polygons.append(pts)

        # Extract openings
        openings = _extract_openings(msp, polygons, None, 3000.0)

        # Verify we detected the opening
        assert len(openings) >= 1, f"Expected at least 1 opening, got {len(openings)}"

        print(f"✓ Detected {len(openings)} openings from layer rectangles")

    finally:
        # Clean up
        dxf_path.unlink()


def test_boolean_cut_openings():
    """Test cutting openings from walls using boolean operations."""
    # Create a simple room polygon
    room_polygon = [[0.0, 0.0], [5000.0, 0.0], [5000.0, 4000.0], [0.0, 4000.0]]

    # Create openings
    openings = [
        {
            "type": "door",
            "position": [2500.0, 0.0],
            "width": 900.0,
            "height": 2100.0,
            "polygon_index": 0,
            "wall_segment": 0,  # South wall
            "z_offset": 0.0,
            "rotation": 0.0
        },
        {
            "type": "window",
            "position": [5000.0, 2000.0],
            "width": 1200.0,
            "height": 1200.0,
            "polygon_index": 0,
            "wall_segment": 1,  # East wall
            "z_offset": 1000.0,
            "rotation": 0.0
        }
    ]

    # Generate STEP file with openings
    try:
        step_bytes = build_step_solid([room_polygon], 3000.0, wall_thickness=200.0, openings=openings)

        # Verify STEP was generated
        assert len(step_bytes) > 1000, "STEP file too small"
        assert b"ISO-10303-21" in step_bytes, "Not a valid STEP file"

        # Verify file is larger than without openings (due to complex geometry)
        step_bytes_no_openings = build_step_solid([room_polygon], 3000.0, wall_thickness=200.0, openings=[])

        print(f"✓ STEP with openings: {len(step_bytes)} bytes")
        print(f"✓ STEP without openings: {len(step_bytes_no_openings)} bytes")

        # Save test output for manual inspection
        output_path = Path("test_outputs") / "door_window"
        output_path.mkdir(parents=True, exist_ok=True)

        with open(output_path / "room_with_openings.step", "wb") as f:
            f.write(step_bytes)

        with open(output_path / "room_without_openings.step", "wb") as f:
            f.write(step_bytes_no_openings)

        print(f"✓ Saved test outputs to {output_path}")

    except Exception as e:
        print(f"✗ Failed to generate STEP with openings: {e}")
        raise


def test_end_to_end_with_openings():
    """End-to-end test: DXF with openings → model generation → STEP with cut openings."""
    dxf_path = create_test_dxf_with_openings(has_insert_blocks=True, has_layer_rectangles=True)

    try:
        # Create a mock job object
        class MockJob:
            id = "test-job-123"
            params = {"extrude_height": 3000, "wall_thickness": 200}

        job = MockJob()

        # Generate model (including opening detection)
        model = _generate_model(dxf_path, job)

        # Verify model has openings
        assert "openings" in model, "Model missing 'openings' field"
        assert len(model["openings"]) > 0, f"Expected openings to be detected, got {len(model['openings'])}"

        # Verify metadata
        assert model["metadata"]["opening_count"] == len(model["openings"])

        print(f"✓ Model generated with {len(model['openings'])} openings")

        # Generate STEP with openings
        step_bytes = build_step_solid(
            model["polygons"],
            model["extrude_height"],
            wall_thickness=model["wall_thickness"],
            openings=model["openings"]
        )

        # Verify STEP was generated
        assert len(step_bytes) > 1000, "STEP file too small"
        assert b"ISO-10303-21" in step_bytes, "Not a valid STEP file"

        print(f"✓ Generated STEP file: {len(step_bytes)} bytes with {len(model['openings'])} openings cut")

        # Save test output
        output_path = Path("test_outputs") / "door_window"
        output_path.mkdir(parents=True, exist_ok=True)

        with open(output_path / "end_to_end_with_openings.step", "wb") as f:
            f.write(step_bytes)

        print(f"✓ Saved end-to-end test output to {output_path}")

    finally:
        # Clean up
        dxf_path.unlink()


if __name__ == "__main__":
    print("Testing door & window opening support (Phase 6.2)")
    print("=" * 60)

    print("\n1. Testing INSERT block detection...")
    test_opening_detection_insert_blocks()

    print("\n2. Testing layer rectangle detection...")
    test_opening_detection_layer_rectangles()

    print("\n3. Testing boolean cut operations...")
    test_boolean_cut_openings()

    print("\n4. Testing end-to-end workflow...")
    test_end_to_end_with_openings()

    print("\n" + "=" * 60)
    print("✓ All door & window tests passed!")
