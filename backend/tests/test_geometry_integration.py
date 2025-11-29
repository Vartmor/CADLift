#!/usr/bin/env python3
"""
Test the updated geometry.py with real cadquery STEP generation
Phase 1.2 integration test
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.pipelines.geometry import build_artifacts
from app.core.errors import CADLiftError


def test_simple_polygon():
    """Test single rectangular room"""
    print("=" * 60)
    print("Test 1: Simple Polygon (Single Room)")
    print("=" * 60)

    # 6m x 4m room
    polygons = [
        [[0, 0], [6000, 0], [6000, 4000], [0, 4000]]
    ]
    height = 3000  # 3m height

    try:
        dxf_bytes, step_bytes = build_artifacts(polygons, height)

        # Save to files
        output_dir = Path("test_outputs/integration")
        output_dir.mkdir(parents=True, exist_ok=True)

        dxf_path = output_dir / "simple_room.dxf"
        step_path = output_dir / "simple_room.step"

        dxf_path.write_bytes(dxf_bytes)
        step_path.write_bytes(step_bytes)

        print(f"✓ DXF generated: {len(dxf_bytes)} bytes → {dxf_path}")
        print(f"✓ STEP generated: {len(step_bytes)} bytes → {step_path}")
        print(f"✓ Test PASSED\n")
        return True
    except Exception as e:
        print(f"✗ Test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_polygons():
    """Test multiple rooms side by side"""
    print("=" * 60)
    print("Test 2: Multiple Polygons (3 Rooms)")
    print("=" * 60)

    # Three rooms in a row
    polygons = [
        [[0, 0], [6000, 0], [6000, 4000], [0, 4000]],  # Room 1
        [[7000, 0], [12000, 0], [12000, 4000], [7000, 4000]],  # Room 2
        [[13000, 0], [17000, 0], [17000, 4000], [13000, 4000]],  # Room 3
    ]
    height = 3000

    try:
        dxf_bytes, step_bytes = build_artifacts(polygons, height)

        output_dir = Path("test_outputs/integration")
        output_dir.mkdir(parents=True, exist_ok=True)

        dxf_path = output_dir / "multiple_rooms.dxf"
        step_path = output_dir / "multiple_rooms.step"

        dxf_path.write_bytes(dxf_bytes)
        step_path.write_bytes(step_bytes)

        print(f"✓ DXF generated: {len(dxf_bytes)} bytes → {dxf_path}")
        print(f"✓ STEP generated: {len(step_bytes)} bytes → {step_path}")
        print(f"✓ Test PASSED\n")
        return True
    except Exception as e:
        print(f"✗ Test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_l_shaped_room():
    """Test L-shaped complex polygon"""
    print("=" * 60)
    print("Test 3: L-Shaped Room (Complex Shape)")
    print("=" * 60)

    # L-shaped room
    polygons = [
        [
            [0, 0],
            [10000, 0],
            [10000, 4000],
            [4000, 4000],
            [4000, 10000],
            [0, 10000],
        ]
    ]
    height = 3000

    try:
        dxf_bytes, step_bytes = build_artifacts(polygons, height)

        output_dir = Path("test_outputs/integration")
        output_dir.mkdir(parents=True, exist_ok=True)

        dxf_path = output_dir / "l_shaped_room.dxf"
        step_path = output_dir / "l_shaped_room.step"

        dxf_path.write_bytes(dxf_bytes)
        step_path.write_bytes(step_bytes)

        print(f"✓ DXF generated: {len(dxf_bytes)} bytes → {dxf_path}")
        print(f"✓ STEP generated: {len(step_bytes)} bytes → {step_path}")
        print(f"✓ Test PASSED\n")
        return True
    except Exception as e:
        print(f"✗ Test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """Test error cases"""
    print("=" * 60)
    print("Test 4: Error Handling")
    print("=" * 60)

    tests_passed = 0
    tests_total = 3

    # Test 1: Empty polygons
    try:
        build_artifacts([], 3000)
        print("✗ Should have raised CADLiftError for empty polygons")
    except CADLiftError as e:
        print(f"✓ Empty polygons error caught: {e}")
        tests_passed += 1

    # Test 2: Invalid height
    try:
        build_artifacts([[[0, 0], [1000, 0], [1000, 1000], [0, 1000]]], 0)
        print("✗ Should have raised CADLiftError for zero height")
    except CADLiftError as e:
        print(f"✓ Zero height error caught: {e}")
        tests_passed += 1

    # Test 3: Polygon with too few points
    try:
        build_artifacts([[[0, 0], [1000, 0]]], 3000)
        print("✗ Should have raised CADLiftError for insufficient points")
    except CADLiftError as e:
        print(f"✓ Insufficient points error caught: {e}")
        tests_passed += 1

    print(f"\n✓ Error handling: {tests_passed}/{tests_total} tests passed\n")
    return tests_passed == tests_total


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("GEOMETRY INTEGRATION TESTS - Phase 1.2")
    print("Testing real cadquery STEP generation")
    print("=" * 60 + "\n")

    results = []

    results.append(("Simple Polygon", test_simple_polygon()))
    results.append(("Multiple Polygons", test_multiple_polygons()))
    results.append(("L-Shaped Room", test_l_shaped_room()))
    results.append(("Error Handling", test_error_handling()))

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:30s}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests PASSED! Phase 1.2 implementation successful!")
        print("\nNext steps:")
        print("1. Test STEP files in FreeCAD/AutoCAD")
        print("2. Run full pipeline integration tests")
        print("3. Test with actual job workflows")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) FAILED. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
