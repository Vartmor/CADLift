#!/usr/bin/env python3
"""
Test script for build123d - Phase 1.1 evaluation
Generates a simple extruded box and exports to STEP
"""

from build123d import *
from pathlib import Path

def test_simple_box():
    """Create a simple 6000x4000x3000mm box"""
    print("Testing build123d - Simple Box")

    # Create a box using build123d
    with BuildPart() as box:
        Box(6000, 4000, 3000)

    # Export to STEP
    output_path = Path("test_outputs/build123d_simple_box.step")
    output_path.parent.mkdir(exist_ok=True)

    export_step(box.part, str(output_path))

    file_size = output_path.stat().st_size
    print(f"✓ Generated: {output_path}")
    print(f"✓ File size: {file_size / 1024:.2f} KB")

    return output_path, file_size


def test_hollow_box_with_walls():
    """Create a hollow box with 200mm wall thickness"""
    print("\nTesting build123d - Hollow Box (Wall Thickness)")

    width, length, height = 6000, 4000, 3000
    wall_thickness = 200

    with BuildPart() as walls:
        # Create outer box
        Box(width, length, height)
        # Offset faces inward and extrude to create hollow interior
        with BuildSketch(Plane.XY.offset(wall_thickness)):
            Rectangle(width - 2*wall_thickness, length - 2*wall_thickness)
        extrude(amount=height - wall_thickness, mode=Mode.SUBTRACT)

    # Export to STEP
    output_path = Path("test_outputs/build123d_hollow_box.step")
    export_step(walls.part, str(output_path))

    file_size = output_path.stat().st_size
    print(f"✓ Generated: {output_path}")
    print(f"✓ File size: {file_size / 1024:.2f} KB")

    return output_path, file_size


def test_multiple_rooms():
    """Create multiple room layout"""
    print("\nTesting build123d - Multiple Rooms")

    rooms = [
        {"x": 0, "y": 0, "width": 6000, "length": 4000},
        {"x": 7000, "y": 0, "width": 5000, "length": 4000},
        {"x": 13000, "y": 0, "width": 4000, "length": 4000},
    ]
    height = 3000

    with BuildPart() as result:
        for room in rooms:
            center_x = room["x"] + room["width"] / 2
            center_y = room["y"] + room["length"] / 2
            with Locations((center_x, center_y, 0)):
                Box(room["width"], room["length"], height)

    # Export to STEP
    output_path = Path("test_outputs/build123d_multiple_rooms.step")
    export_step(result.part, str(output_path))

    file_size = output_path.stat().st_size
    print(f"✓ Generated: {output_path}")
    print(f"✓ File size: {file_size / 1024:.2f} KB")

    return output_path, file_size


def test_l_shaped_room():
    """Create L-shaped room layout"""
    print("\nTesting build123d - L-Shaped Room")

    with BuildPart() as l_shape:
        # First rectangle
        Box(10000, 4000, 3000)
        # Second rectangle forming the L
        with Locations((3000, 5000, 0)):
            Box(4000, 6000, 3000)

    # Export to STEP
    output_path = Path("test_outputs/build123d_l_shaped.step")
    export_step(l_shape.part, str(output_path))

    file_size = output_path.stat().st_size
    print(f"✓ Generated: {output_path}")
    print(f"✓ File size: {file_size / 1024:.2f} KB")

    return output_path, file_size


if __name__ == "__main__":
    print("=" * 60)
    print("build123d Evaluation - Phase 1.1")
    print("=" * 60)

    try:
        results = []

        # Test 1: Simple box
        path1, size1 = test_simple_box()
        results.append(("Simple Box", size1))

        # Test 2: Hollow box with walls
        path2, size2 = test_hollow_box_with_walls()
        results.append(("Hollow Box (Walls)", size2))

        # Test 3: Multiple rooms
        path3, size3 = test_multiple_rooms()
        results.append(("Multiple Rooms", size3))

        # Test 4: L-shaped room
        path4, size4 = test_l_shaped_room()
        results.append(("L-Shaped Room", size4))

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        for name, size in results:
            print(f"{name:25s}: {size / 1024:8.2f} KB")

        avg_size = sum(r[1] for r in results) / len(results)
        print(f"\nAverage file size: {avg_size / 1024:.2f} KB")
        print("\n✅ All build123d tests passed!")
        print("Next step: Compare with cadquery results")

    except Exception as e:
        print(f"\n❌ Error during build123d testing: {e}")
        import traceback
        traceback.print_exc()
