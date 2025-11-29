"""
Tests for parametric component library (Phase 6.5).

Tests door, window, and furniture component generation.
"""

import tempfile
from pathlib import Path
import cadquery as cq

from app.components import (
    ParametricDoor,
    ParametricWindow,
    FurnitureLibrary,
    place_component,
    check_collision
)


def test_parametric_door_single():
    """Test single door generation."""
    door = ParametricDoor(width=900.0, height=2100.0, door_type="single")

    solid = door.generate()

    # Verify it's a valid CadQuery object
    assert isinstance(solid, cq.Workplane)

    # Verify it has geometry
    bbox = solid.val().BoundingBox()
    assert bbox.xlen > 800, "Door width too small"
    assert bbox.zlen > 2000, "Door height too small"

    print(f"✓ Generated single door: {bbox.xlen:.0f}x{bbox.ylen:.0f}x{bbox.zlen:.0f}mm")

    # Export to STEP for manual inspection
    output_path = Path("test_outputs") / "components"
    output_path.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as tmp:
        cq.exporters.export(solid, tmp.name, "STEP")
        step_bytes = Path(tmp.name).read_bytes()
        Path(tmp.name).unlink()

    (output_path / "door_single.step").write_bytes(step_bytes)
    print(f"✓ Saved single door to {output_path}/door_single.step")


def test_parametric_door_double():
    """Test double door generation."""
    door = ParametricDoor(width=1800.0, height=2100.0, door_type="double")

    solid = door.generate()

    # Verify geometry
    bbox = solid.val().BoundingBox()
    assert bbox.xlen > 1700, "Double door width too small"
    assert bbox.zlen > 2000, "Door height too small"

    print(f"✓ Generated double door: {bbox.xlen:.0f}x{bbox.ylen:.0f}x{bbox.zlen:.0f}mm")

    # Export
    output_path = Path("test_outputs") / "components"
    output_path.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as tmp:
        cq.exporters.export(solid, tmp.name, "STEP")
        step_bytes = Path(tmp.name).read_bytes()
        Path(tmp.name).unlink()

    (output_path / "door_double.step").write_bytes(step_bytes)
    print(f"✓ Saved double door to {output_path}/door_double.step")


def test_parametric_window():
    """Test window generation."""
    window = ParametricWindow(width=1200.0, height=1200.0, window_type="fixed", mullions=2)

    solid = window.generate()

    # Verify geometry
    bbox = solid.val().BoundingBox()
    assert bbox.xlen > 1100, "Window width too small"
    assert bbox.zlen > 1100, "Window height too small"

    print(f"✓ Generated window with mullions: {bbox.xlen:.0f}x{bbox.ylen:.0f}x{bbox.zlen:.0f}mm")

    # Export
    output_path = Path("test_outputs") / "components"
    output_path.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as tmp:
        cq.exporters.export(solid, tmp.name, "STEP")
        step_bytes = Path(tmp.name).read_bytes()
        Path(tmp.name).unlink()

    (output_path / "window_fixed.step").write_bytes(step_bytes)
    print(f"✓ Saved window to {output_path}/window_fixed.step")


def test_furniture_desk():
    """Test desk generation."""
    desk = FurnitureLibrary.generate_desk(width=1500.0, depth=750.0, height=750.0)

    # Verify geometry
    bbox = desk.val().BoundingBox()
    assert bbox.xlen > 1400, "Desk width too small"
    assert bbox.ylen > 700, "Desk depth too small"
    assert bbox.zlen > 700, "Desk height too small"

    print(f"✓ Generated desk: {bbox.xlen:.0f}x{bbox.ylen:.0f}x{bbox.zlen:.0f}mm")

    # Export
    output_path = Path("test_outputs") / "components"
    output_path.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as tmp:
        cq.exporters.export(desk, tmp.name, "STEP")
        step_bytes = Path(tmp.name).read_bytes()
        Path(tmp.name).unlink()

    (output_path / "desk.step").write_bytes(step_bytes)
    print(f"✓ Saved desk to {output_path}/desk.step")


def test_furniture_chair():
    """Test chair generation."""
    chair = FurnitureLibrary.generate_chair(width=450.0, depth=450.0, seat_height=450.0)

    # Verify geometry
    bbox = chair.val().BoundingBox()
    assert bbox.xlen > 400, "Chair width too small"
    assert bbox.zlen > 400, "Chair height too small"

    print(f"✓ Generated chair: {bbox.xlen:.0f}x{bbox.ylen:.0f}x{bbox.zlen:.0f}mm")

    # Export
    output_path = Path("test_outputs") / "components"
    output_path.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as tmp:
        cq.exporters.export(chair, tmp.name, "STEP")
        step_bytes = Path(tmp.name).read_bytes()
        Path(tmp.name).unlink()

    (output_path / "chair.step").write_bytes(step_bytes)
    print(f"✓ Saved chair to {output_path}/chair.step")


def test_furniture_bed():
    """Test bed generation."""
    bed = FurnitureLibrary.generate_bed(width=2000.0, length=1500.0, mattress_height=500.0)

    # Verify geometry
    bbox = bed.val().BoundingBox()
    assert bbox.xlen > 1400, "Bed length too small"
    assert bbox.ylen > 1900, "Bed width too small"
    assert bbox.zlen > 400, "Bed height too small"

    print(f"✓ Generated bed: {bbox.xlen:.0f}x{bbox.ylen:.0f}x{bbox.zlen:.0f}mm")

    # Export
    output_path = Path("test_outputs") / "components"
    output_path.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as tmp:
        cq.exporters.export(bed, tmp.name, "STEP")
        step_bytes = Path(tmp.name).read_bytes()
        Path(tmp.name).unlink()

    (output_path / "bed.step").write_bytes(step_bytes)
    print(f"✓ Saved bed to {output_path}/bed.step")


def test_furniture_table():
    """Test table generation."""
    table = FurnitureLibrary.generate_table(diameter=1000.0, height=750.0)

    # Verify geometry
    bbox = table.val().BoundingBox()
    assert bbox.xlen > 900, "Table diameter too small"
    assert bbox.zlen > 700, "Table height too small"

    print(f"✓ Generated table: diameter≈{bbox.xlen:.0f}mm, height={bbox.zlen:.0f}mm")

    # Export
    output_path = Path("test_outputs") / "components"
    output_path.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as tmp:
        cq.exporters.export(table, tmp.name, "STEP")
        step_bytes = Path(tmp.name).read_bytes()
        Path(tmp.name).unlink()

    (output_path / "table.step").write_bytes(step_bytes)
    print(f"✓ Saved table to {output_path}/table.step")


def test_component_placement():
    """Test placing components at specific positions."""
    # Create a simple chair
    chair = FurnitureLibrary.generate_chair(width=450.0, depth=450.0, seat_height=450.0)

    # Get original bounding box
    original_bbox = chair.val().BoundingBox()

    # Place at specific position (without rotation first)
    positioned_chair = place_component(chair, position=(1000.0, 2000.0, 0.0), rotation=0.0)

    # Verify it's been moved
    bbox = positioned_chair.val().BoundingBox()
    assert bbox.xmin > 900, f"Chair not moved to correct X position: {bbox.xmin}"
    assert bbox.ymin > 1900, f"Chair not moved to correct Y position: {bbox.ymin}"

    print(f"✓ Placed chair at (1000, 2000, 0)")
    print(f"  Original bbox center: ({original_bbox.center.x:.0f}, {original_bbox.center.y:.0f}, {original_bbox.center.z:.0f})")
    print(f"  New bbox: ({bbox.xmin:.0f}, {bbox.ymin:.0f}, {bbox.zmin:.0f}) to ({bbox.xmax:.0f}, {bbox.ymax:.0f}, {bbox.zmax:.0f})")

    # Test with rotation
    positioned_rotated = place_component(chair, position=(5000.0, 5000.0, 0.0), rotation=90.0)
    bbox_rotated = positioned_rotated.val().BoundingBox()

    print(f"✓ Placed chair at (5000, 5000, 0) with 90° rotation")
    print(f"  Rotated bbox: ({bbox_rotated.xmin:.0f}, {bbox_rotated.ymin:.0f}, {bbox_rotated.zmin:.0f}) to ({bbox_rotated.xmax:.0f}, {bbox_rotated.ymax:.0f}, {bbox_rotated.zmax:.0f})")


def test_collision_detection():
    """Test collision detection between components."""
    # Create two desks
    desk1 = FurnitureLibrary.generate_desk(width=1500.0, depth=750.0, height=750.0)
    desk2 = FurnitureLibrary.generate_desk(width=1500.0, depth=750.0, height=750.0)

    # Place second desk away from first (no collision)
    desk2_placed = place_component(desk2, position=(2000.0, 0.0, 0.0))

    collision1 = check_collision(desk1, desk2_placed)
    assert not collision1, "False positive: desks should not collide"

    print("✓ No collision detected for separated desks")

    # Place second desk overlapping first (collision)
    desk2_overlapping = place_component(desk2, position=(500.0, 0.0, 0.0))

    collision2 = check_collision(desk1, desk2_overlapping)
    assert collision2, "False negative: desks should collide"

    print("✓ Collision detected for overlapping desks")


if __name__ == "__main__":
    print("Testing parametric component library (Phase 6.5)")
    print("=" * 60)

    print("\n1. Testing single door...")
    test_parametric_door_single()

    print("\n2. Testing double door...")
    test_parametric_door_double()

    print("\n3. Testing window with mullions...")
    test_parametric_window()

    print("\n4. Testing desk generation...")
    test_furniture_desk()

    print("\n5. Testing chair generation...")
    test_furniture_chair()

    print("\n6. Testing bed generation...")
    test_furniture_bed()

    print("\n7. Testing table generation...")
    test_furniture_table()

    print("\n8. Testing component placement...")
    test_component_placement()

    print("\n9. Testing collision detection...")
    test_collision_detection()

    print("\n" + "=" * 60)
    print("✓ All component tests passed!")
