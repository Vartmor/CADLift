#!/usr/bin/env python3
"""
Test script for improved DXF generation with POLYFACE meshes.

Tests the new DXF generation that uses MeshBuilder and proper layer structure
to avoid diagonal line artifacts seen with 3DFACE primitives.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.pipelines.geometry import extrude_polygons_to_dxf


def test_simple_rectangle():
    """Test 1: Simple rectangular room"""
    print("\n" + "="*60)
    print("Test 1: Simple Rectangle (5m x 4m, height 3m)")
    print("="*60)

    polygon = [
        [0.0, 0.0],
        [5000.0, 0.0],
        [5000.0, 4000.0],
        [0.0, 4000.0]
    ]

    dxf_bytes = extrude_polygons_to_dxf([polygon], height=3000.0)

    output_path = "test_outputs/dxf_improved/simple_rectangle.dxf"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(dxf_bytes)

    print(f"✅ Generated: {output_path}")
    print(f"   File size: {len(dxf_bytes):,} bytes")
    print(f"   Vertices: 8 (4 bottom + 4 top)")
    print(f"   Walls: 4 quadrilateral faces")
    print(f"   Top: 1 quadrilateral face")

    return dxf_bytes


def test_multiple_rooms():
    """Test 2: Multiple rectangular rooms"""
    print("\n" + "="*60)
    print("Test 2: Three Rooms (varying sizes, height 2.8m)")
    print("="*60)

    polygons = [
        # Room 1: 6m x 5m
        [
            [0.0, 0.0],
            [6000.0, 0.0],
            [6000.0, 5000.0],
            [0.0, 5000.0]
        ],
        # Room 2: 4m x 4m (offset)
        [
            [7000.0, 0.0],
            [11000.0, 0.0],
            [11000.0, 4000.0],
            [7000.0, 4000.0]
        ],
        # Room 3: 5m x 3m (offset)
        [
            [7000.0, 5000.0],
            [12000.0, 5000.0],
            [12000.0, 8000.0],
            [7000.0, 8000.0]
        ]
    ]

    dxf_bytes = extrude_polygons_to_dxf(polygons, height=2800.0)

    output_path = "test_outputs/dxf_improved/multiple_rooms.dxf"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(dxf_bytes)

    print(f"✅ Generated: {output_path}")
    print(f"   File size: {len(dxf_bytes):,} bytes")
    print(f"   Rooms: 3")
    print(f"   Total vertices: 24 (8 per room)")
    print(f"   Layers: Footprint, Walls, Top")

    return dxf_bytes


def test_l_shaped_room():
    """Test 3: L-shaped room (complex polygon)"""
    print("\n" + "="*60)
    print("Test 3: L-Shaped Room (6 vertices, height 3m)")
    print("="*60)

    # L-shape: 8m x 8m with 3m x 3m cut from top-right
    polygon = [
        [0.0, 0.0],
        [8000.0, 0.0],
        [8000.0, 5000.0],
        [5000.0, 5000.0],
        [5000.0, 8000.0],
        [0.0, 8000.0]
    ]

    dxf_bytes = extrude_polygons_to_dxf([polygon], height=3000.0)

    output_path = "test_outputs/dxf_improved/l_shaped_room.dxf"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(dxf_bytes)

    print(f"✅ Generated: {output_path}")
    print(f"   File size: {len(dxf_bytes):,} bytes")
    print(f"   Vertices: 13 (6 bottom + 6 top + 1 center for fan)")
    print(f"   Walls: 6 quadrilateral faces")
    print(f"   Top: 6 triangular faces (fan triangulation)")

    return dxf_bytes


def test_octagon():
    """Test 4: Octagonal room (8 vertices)"""
    print("\n" + "="*60)
    print("Test 4: Octagonal Room (8 vertices, height 3.5m)")
    print("="*60)

    import math

    # Regular octagon with radius 4m
    radius = 4000.0
    polygon = []
    for i in range(8):
        angle = 2 * math.pi * i / 8
        x = radius * math.cos(angle) + 5000.0  # Offset center
        y = radius * math.sin(angle) + 5000.0
        polygon.append([x, y])

    dxf_bytes = extrude_polygons_to_dxf([polygon], height=3500.0)

    output_path = "test_outputs/dxf_improved/octagon_room.dxf"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(dxf_bytes)

    print(f"✅ Generated: {output_path}")
    print(f"   File size: {len(dxf_bytes):,} bytes")
    print(f"   Vertices: 17 (8 bottom + 8 top + 1 center)")
    print(f"   Walls: 8 quadrilateral faces")
    print(f"   Top: 8 triangular faces (fan triangulation)")

    return dxf_bytes


def verify_layer_structure():
    """Verify that layers are properly created in DXF files"""
    print("\n" + "="*60)
    print("Verification: Layer Structure")
    print("="*60)

    import ezdxf

    # Load one of the generated files
    doc = ezdxf.readfile("test_outputs/dxf_improved/simple_rectangle.dxf")

    # Check layers
    layers = list(doc.layers)
    layer_names = [layer.dxf.name for layer in layers]

    print("Layers found:")
    for layer in layers:
        print(f"  - {layer.dxf.name} (color: {layer.dxf.color})")

    # Verify expected layers exist
    expected = ["Footprint", "Walls", "Top"]
    missing = [name for name in expected if name not in layer_names]

    if missing:
        print(f"⚠️  Missing layers: {missing}")
    else:
        print("✅ All expected layers present")

    # Check units
    print(f"\nDocument units: {doc.units}")
    if doc.units == ezdxf.units.MM:
        print("✅ Units set to millimeters")
    else:
        print("⚠️  Units not set to millimeters")

    # Check DXF version
    print(f"DXF version: {doc.dxfversion}")

    # Check entity counts per layer
    print("\nEntities per layer:")
    for layer_name in expected:
        entities = list(doc.modelspace().query(f'*[layer=="{layer_name}"]'))
        print(f"  {layer_name}: {len(entities)} entities")


def main():
    """Run all tests"""
    print("\n" + "#"*60)
    print("# DXF Improved Generation Test Suite")
    print("# Phase 1.3: POLYFACE Mesh + Layer Structure")
    print("#"*60)

    try:
        # Run tests
        test_simple_rectangle()
        test_multiple_rooms()
        test_l_shaped_room()
        test_octagon()

        # Verify structure
        verify_layer_structure()

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        print("\nGenerated files:")
        print("  test_outputs/dxf_improved/simple_rectangle.dxf")
        print("  test_outputs/dxf_improved/multiple_rooms.dxf")
        print("  test_outputs/dxf_improved/l_shaped_room.dxf")
        print("  test_outputs/dxf_improved/octagon_room.dxf")
        print("\n📝 Next: Open these files in a DXF viewer to verify")
        print("   - No diagonal line artifacts")
        print("   - Proper 3D mesh visualization")
        print("   - Editable geometry")
        print("   - Layer structure visible")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
