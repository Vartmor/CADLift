#!/usr/bin/env python3
"""
Test script for cadquery - Phase 1.1 evaluation
Generates a simple extruded box and exports to STEP
"""

import cadquery as cq
from pathlib import Path

def test_simple_box():
    """Create a simple 6000x4000x3000mm box"""
    print("Testing cadquery - Simple Box")

    # Create a box using cadquery
    box = (
        cq.Workplane("XY")
        .rect(6000, 4000)
        .extrude(3000)
    )

    # Export to STEP
    output_path = Path("test_outputs/cadquery_simple_box.step")
    output_path.parent.mkdir(exist_ok=True)

    cq.exporters.export(box, str(output_path))

    file_size = output_path.stat().st_size
    print(f"✓ Generated: {output_path}")
    print(f"✓ File size: {file_size / 1024:.2f} KB")

    return output_path, file_size


def test_hollow_box_with_walls():
    """Create a hollow box with 200mm wall thickness"""
    print("\nTesting cadquery - Hollow Box (Wall Thickness)")

    # Outer dimensions
    width, length, height = 6000, 4000, 3000
    wall_thickness = 200

    # Create outer box
    outer = (
        cq.Workplane("XY")
        .rect(width, length)
        .extrude(height)
    )

    # Create inner box (offset by wall thickness)
    inner = (
        cq.Workplane("XY")
        .workplane(offset=wall_thickness)  # Start above base
        .rect(width - 2*wall_thickness, length - 2*wall_thickness)
        .extrude(height - wall_thickness)
    )

    # Subtract inner from outer to create walls
    walls = outer.cut(inner)

    # Export to STEP
    output_path = Path("test_outputs/cadquery_hollow_box.step")
    cq.exporters.export(walls, str(output_path))

    file_size = output_path.stat().st_size
    print(f"✓ Generated: {output_path}")
    print(f"✓ File size: {file_size / 1024:.2f} KB")

    return output_path, file_size


def test_multiple_rooms():
    """Create multiple room layout"""
    print("\nTesting cadquery - Multiple Rooms")

    # Define rooms
    rooms = [
        {"x": 0, "y": 0, "width": 6000, "length": 4000},
        {"x": 7000, "y": 0, "width": 5000, "length": 4000},
        {"x": 13000, "y": 0, "width": 4000, "length": 4000},
    ]
    height = 3000

    # Create first room
    result = (
        cq.Workplane("XY")
        .workplane(offset=0, origin=(rooms[0]["x"] + rooms[0]["width"]/2,
                                      rooms[0]["y"] + rooms[0]["length"]/2, 0))
        .rect(rooms[0]["width"], rooms[0]["length"])
        .extrude(height)
    )

    # Add other rooms
    for room in rooms[1:]:
        new_room = (
            cq.Workplane("XY")
            .workplane(offset=0, origin=(room["x"] + room["width"]/2,
                                          room["y"] + room["length"]/2, 0))
            .rect(room["width"], room["length"])
            .extrude(height)
        )
        result = result.union(new_room)

    # Export to STEP
    output_path = Path("test_outputs/cadquery_multiple_rooms.step")
    cq.exporters.export(result, str(output_path))

    file_size = output_path.stat().st_size
    print(f"✓ Generated: {output_path}")
    print(f"✓ File size: {file_size / 1024:.2f} KB")

    return output_path, file_size


def test_l_shaped_room():
    """Create L-shaped room layout"""
    print("\nTesting cadquery - L-Shaped Room")

    # Create two rectangles that form an L
    part1 = (
        cq.Workplane("XY")
        .rect(10000, 4000)
        .extrude(3000)
    )

    part2 = (
        cq.Workplane("XY")
        .workplane(offset=0, origin=(3000, 5000, 0))
        .rect(4000, 6000)
        .extrude(3000)
    )

    # Union to create L-shape
    l_shape = part1.union(part2)

    # Export to STEP
    output_path = Path("test_outputs/cadquery_l_shaped.step")
    cq.exporters.export(l_shape, str(output_path))

    file_size = output_path.stat().st_size
    print(f"✓ Generated: {output_path}")
    print(f"✓ File size: {file_size / 1024:.2f} KB")

    return output_path, file_size


if __name__ == "__main__":
    print("=" * 60)
    print("CadQuery Evaluation - Phase 1.1")
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
        print("\n✅ All cadquery tests passed!")
        print("Next step: Test in FreeCAD/AutoCAD to verify compatibility")

    except Exception as e:
        print(f"\n❌ Error during cadquery testing: {e}")
        import traceback
        traceback.print_exc()
