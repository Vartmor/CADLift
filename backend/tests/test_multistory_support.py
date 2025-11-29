"""
Tests for multi-story building support (Phase 6.3).

Tests the generation of multi-story buildings with proper Z-stacking.
"""

import tempfile
from pathlib import Path

from app.pipelines.geometry import (
    build_step_solid_multistory,
    build_artifacts_multistory,
    extrude_polygons_to_dxf_multistory
)
import ezdxf


def test_multistory_step_generation():
    """Test STEP generation for multi-story buildings."""
    # Create 3-story building
    floors = [
        {
            "level": 0,
            "polygons": [[[0.0, 0.0], [5000.0, 0.0], [5000.0, 4000.0], [0.0, 4000.0]]],
            "height": 3000.0,
            "z_offset": 0.0
        },
        {
            "level": 1,
            "polygons": [[[0.0, 0.0], [5000.0, 0.0], [5000.0, 4000.0], [0.0, 4000.0]]],
            "height": 3000.0,
            "z_offset": 3000.0
        },
        {
            "level": 2,
            "polygons": [[[0.0, 0.0], [5000.0, 0.0], [5000.0, 4000.0], [0.0, 4000.0]]],
            "height": 3500.0,  # Different height for top floor
            "z_offset": 6000.0
        }
    ]

    # Generate STEP
    step_bytes = build_step_solid_multistory(floors, wall_thickness=200.0)

    # Verify STEP was generated
    assert len(step_bytes) > 1000, "STEP file too small"
    assert b"ISO-10303-21" in step_bytes, "Not a valid STEP file"

    print(f"✓ Generated multi-story STEP: {len(step_bytes)} bytes for 3 floors")

    # Save test output
    output_path = Path("test_outputs") / "multistory"
    output_path.mkdir(parents=True, exist_ok=True)

    with open(output_path / "3_story_building.step", "wb") as f:
        f.write(step_bytes)

    print(f"✓ Saved 3-story building to {output_path}")


def test_multistory_dxf_generation():
    """Test DXF generation for multi-story buildings with floor layers."""
    floors = [
        {
            "level": 0,
            "polygons": [[[0.0, 0.0], [5000.0, 0.0], [5000.0, 4000.0], [0.0, 4000.0]]],
            "height": 3000.0,
            "z_offset": 0.0
        },
        {
            "level": 1,
            "polygons": [[[0.0, 0.0], [4000.0, 0.0], [4000.0, 3500.0], [0.0, 3500.0]]],
            "height": 3000.0,
            "z_offset": 3000.0
        }
    ]

    # Generate DXF
    dxf_bytes = extrude_polygons_to_dxf_multistory(floors)

    # Verify DXF was generated
    assert len(dxf_bytes) > 500, "DXF file too small"

    # Parse DXF and verify layers
    with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tmp_file:
        tmp_file.write(dxf_bytes)
        tmp_path = tmp_file.name

    try:
        doc = ezdxf.readfile(tmp_path)

        # Verify floor layers exist
        layer_names = [layer.dxf.name for layer in doc.layers]

        assert "FLOOR-0-Footprint" in layer_names, "Missing FLOOR-0-Footprint layer"
        assert "FLOOR-0-Walls" in layer_names, "Missing FLOOR-0-Walls layer"
        assert "FLOOR-1-Footprint" in layer_names, "Missing FLOOR-1-Footprint layer"
        assert "FLOOR-1-Walls" in layer_names, "Missing FLOOR-1-Walls layer"

        print(f"✓ Generated multi-story DXF with layers: {', '.join(layer_names)}")

        # Verify entities on layers
        msp = doc.modelspace()
        floor_0_entities = list(msp.query('*[layer=="FLOOR-0-Footprint"]'))
        floor_1_entities = list(msp.query('*[layer=="FLOOR-1-Footprint"]'))

        assert len(floor_0_entities) > 0, "No entities on FLOOR-0-Footprint"
        assert len(floor_1_entities) > 0, "No entities on FLOOR-1-Footprint"

        print(f"✓ Floor 0: {len(floor_0_entities)} entities, Floor 1: {len(floor_1_entities)} entities")

    finally:
        Path(tmp_path).unlink()


def test_multistory_with_openings():
    """Test multi-story buildings with door/window openings on different floors."""
    floors = [
        {
            "level": 0,
            "polygons": [[[0.0, 0.0], [5000.0, 0.0], [5000.0, 4000.0], [0.0, 4000.0]]],
            "height": 3000.0,
            "z_offset": 0.0
        },
        {
            "level": 1,
            "polygons": [[[0.0, 0.0], [5000.0, 0.0], [5000.0, 4000.0], [0.0, 4000.0]]],
            "height": 3000.0,
            "z_offset": 3000.0
        }
    ]

    # Openings on different floors
    openings = [
        {
            "type": "door",
            "position": [2500.0, 0.0],
            "width": 900.0,
            "height": 2100.0,
            "polygon_index": 0,
            "wall_segment": 0,
            "z_offset": 0.0,
            "floor_level": 0,
            "rotation": 0.0
        },
        {
            "type": "window",
            "position": [2500.0, 0.0],
            "width": 1200.0,
            "height": 1200.0,
            "polygon_index": 0,
            "wall_segment": 0,
            "z_offset": 1000.0,
            "floor_level": 1,
            "rotation": 0.0
        }
    ]

    # Generate STEP with openings
    step_bytes = build_step_solid_multistory(floors, wall_thickness=200.0, openings=openings)

    # Verify STEP was generated
    assert len(step_bytes) > 1000, "STEP file too small"
    assert b"ISO-10303-21" in step_bytes, "Not a valid STEP file"

    print(f"✓ Generated multi-story STEP with openings: {len(step_bytes)} bytes")

    # Save test output
    output_path = Path("test_outputs") / "multistory"
    output_path.mkdir(parents=True, exist_ok=True)

    with open(output_path / "2_story_with_openings.step", "wb") as f:
        f.write(step_bytes)

    print(f"✓ Saved 2-story building with openings to {output_path}")


def test_multistory_artifacts():
    """Test complete artifact generation (DXF + STEP) for multi-story buildings."""
    floors = [
        {
            "level": 0,
            "polygons": [
                [[0.0, 0.0], [5000.0, 0.0], [5000.0, 4000.0], [0.0, 4000.0]],
                [[6000.0, 0.0], [9000.0, 0.0], [9000.0, 3000.0], [6000.0, 3000.0]]
            ],
            "height": 3000.0,
            "z_offset": 0.0
        },
        {
            "level": 1,
            "polygons": [
                [[0.0, 0.0], [5000.0, 0.0], [5000.0, 4000.0], [0.0, 4000.0]]
            ],
            "height": 3000.0,
            "z_offset": 3000.0
        }
    ]

    # Generate both artifacts
    dxf_bytes, step_bytes = build_artifacts_multistory(floors, wall_thickness=200.0)

    # Verify both were generated
    assert len(dxf_bytes) > 500, "DXF file too small"
    assert len(step_bytes) > 1000, "STEP file too small"
    assert b"ISO-10303-21" in step_bytes, "Not a valid STEP file"

    print(f"✓ Generated multi-story artifacts: DXF={len(dxf_bytes)} bytes, STEP={len(step_bytes)} bytes")

    # Save test outputs
    output_path = Path("test_outputs") / "multistory"
    output_path.mkdir(parents=True, exist_ok=True)

    with open(output_path / "complex_multistory.dxf", "wb") as f:
        f.write(dxf_bytes)

    with open(output_path / "complex_multistory.step", "wb") as f:
        f.write(step_bytes)

    print(f"✓ Saved complex multi-story building to {output_path}")


def test_variable_floor_heights():
    """Test buildings with variable floor heights."""
    floors = [
        {
            "level": 0,
            "polygons": [[[0.0, 0.0], [5000.0, 0.0], [5000.0, 4000.0], [0.0, 4000.0]]],
            "height": 4000.0,  # Tall ground floor
            "z_offset": 0.0
        },
        {
            "level": 1,
            "polygons": [[[0.0, 0.0], [5000.0, 0.0], [5000.0, 4000.0], [0.0, 4000.0]]],
            "height": 3000.0,  # Standard floor
            "z_offset": 4000.0
        },
        {
            "level": 2,
            "polygons": [[[0.0, 0.0], [5000.0, 0.0], [5000.0, 4000.0], [0.0, 4000.0]]],
            "height": 2500.0,  # Shorter top floor
            "z_offset": 7000.0
        }
    ]

    # Generate STEP
    step_bytes = build_step_solid_multistory(floors, wall_thickness=200.0)

    # Verify STEP was generated
    assert len(step_bytes) > 1000, "STEP file too small"
    assert b"ISO-10303-21" in step_bytes, "Not a valid STEP file"

    # Calculate total building height
    total_height = sum(floor["height"] for floor in floors)
    print(f"✓ Generated building with variable heights: total {total_height}mm = {total_height/1000}m")

    # Save test output
    output_path = Path("test_outputs") / "multistory"
    output_path.mkdir(parents=True, exist_ok=True)

    with open(output_path / "variable_heights.step", "wb") as f:
        f.write(step_bytes)

    print(f"✓ Saved variable-height building to {output_path}")


if __name__ == "__main__":
    print("Testing multi-story building support (Phase 6.3)")
    print("=" * 60)

    print("\n1. Testing multi-story STEP generation...")
    test_multistory_step_generation()

    print("\n2. Testing multi-story DXF generation with floor layers...")
    test_multistory_dxf_generation()

    print("\n3. Testing multi-story with openings...")
    test_multistory_with_openings()

    print("\n4. Testing complete artifact generation...")
    test_multistory_artifacts()

    print("\n5. Testing variable floor heights...")
    test_variable_floor_heights()

    print("\n" + "=" * 60)
    print("✓ All multi-story tests passed!")
