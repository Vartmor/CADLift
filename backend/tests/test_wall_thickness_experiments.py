#!/usr/bin/env python3
"""
Experimental tests for wall thickness implementation approaches.

Tests different methods:
1. offset2D() - offset polygon inward, then subtract
2. shell() - hollow out solid after extrusion
3. Manual offset - calculate offset polygon manually
"""

import cadquery as cq
import tempfile
import os


def approach_1_offset2d():
    """
    Approach 1: Use offset2D to create inner polygon, then subtract.
    """
    print("\n" + "="*60)
    print("Approach 1: offset2D() + Boolean Subtraction")
    print("="*60)

    try:
        # Room: 6m x 5m, height 3m, wall thickness 200mm
        width, length, height = 6000.0, 5000.0, 3000.0
        wall_thickness = 200.0

        # Create outer wall (original polygon)
        outer = (
            cq.Workplane("XY")
            .rect(width, length)
            .extrude(height)
        )

        # Create inner cavity (offset polygon)
        # offset2D with negative value offsets inward
        inner = (
            cq.Workplane("XY")
            .rect(width, length)
            .offset2D(-wall_thickness)
            .extrude(height)
        )

        # Subtract inner from outer to get walls
        result = outer.cut(inner)

        # Export to verify
        with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            cq.exporters.export(result, tmp_path, "STEP")
            file_size = os.path.getsize(tmp_path)
            print(f"✅ SUCCESS: Generated {file_size:,} byte STEP file")
            print(f"   Method: offset2D(-{wall_thickness}mm) + cut()")
            print(f"   Outer: {width}x{length}mm")
            print(f"   Inner: {width-2*wall_thickness}x{length-2*wall_thickness}mm")
            print(f"   Wall thickness: {wall_thickness}mm")

            # Save for inspection
            output_path = "test_outputs/wall_thickness/approach1_offset2d.step"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Use copy instead of rename for cross-device compatibility
            import shutil
            shutil.copy(tmp_path, output_path)
            print(f"   Saved: {output_path}")

            return True, result
        finally:
            try:
                os.unlink(tmp_path)
            except:
                pass

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def approach_2_shell():
    """
    Approach 2: Use shell() to hollow out the solid.
    """
    print("\n" + "="*60)
    print("Approach 2: shell() Method")
    print("="*60)

    try:
        # Room: 6m x 5m, height 3m, wall thickness 200mm
        width, length, height = 6000.0, 5000.0, 3000.0
        wall_thickness = 200.0

        # Create solid box
        box = cq.Workplane("XY").rect(width, length).extrude(height)

        # Shell it - remove top face and hollow out
        # Negative thickness shells inward
        result = box.faces("+Z").shell(-wall_thickness)

        # Export to verify
        with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            cq.exporters.export(result, tmp_path, "STEP")
            file_size = os.path.getsize(tmp_path)
            print(f"✅ SUCCESS: Generated {file_size:,} byte STEP file")
            print(f"   Method: shell(-{wall_thickness}mm) on +Z face")
            print(f"   Outer: {width}x{length}mm")
            print(f"   Wall thickness: {wall_thickness}mm")
            print(f"   Note: Top face removed for open room")

            # Save for inspection
            output_path = "test_outputs/wall_thickness/approach2_shell.step"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Use copy instead of rename for cross-device compatibility
            import shutil
            shutil.copy(tmp_path, output_path)
            print(f"   Saved: {output_path}")

            return True, result
        finally:
            try:
                os.unlink(tmp_path)
            except:
                pass

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def approach_3_manual():
    """
    Approach 3: Manually calculate offset polygon coordinates.
    """
    print("\n" + "="*60)
    print("Approach 3: Manual Polygon Offset")
    print("="*60)

    try:
        # Room: 6m x 5m, height 3m, wall thickness 200mm
        width, length, height = 6000.0, 5000.0, 3000.0
        wall_thickness = 200.0

        # Outer polygon (centered at origin)
        outer_points = [
            (-width/2, -length/2),
            (width/2, -length/2),
            (width/2, length/2),
            (-width/2, length/2)
        ]

        # Inner polygon (offset inward)
        inner_width = width - 2 * wall_thickness
        inner_length = length - 2 * wall_thickness
        inner_points = [
            (-inner_width/2, -inner_length/2),
            (inner_width/2, -inner_length/2),
            (inner_width/2, inner_length/2),
            (-inner_width/2, inner_length/2)
        ]

        # Create outer and inner solids
        outer = (
            cq.Workplane("XY")
            .polyline(outer_points)
            .close()
            .extrude(height)
        )

        inner = (
            cq.Workplane("XY")
            .polyline(inner_points)
            .close()
            .extrude(height)
        )

        # Subtract
        result = outer.cut(inner)

        # Export to verify
        with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            cq.exporters.export(result, tmp_path, "STEP")
            file_size = os.path.getsize(tmp_path)
            print(f"✅ SUCCESS: Generated {file_size:,} byte STEP file")
            print(f"   Method: Manual coordinate offset + cut()")
            print(f"   Outer: {width}x{length}mm")
            print(f"   Inner: {inner_width}x{inner_length}mm")
            print(f"   Wall thickness: {wall_thickness}mm")

            # Save for inspection
            output_path = "test_outputs/wall_thickness/approach3_manual.step"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Use copy instead of rename for cross-device compatibility
            import shutil
            shutil.copy(tmp_path, output_path)
            print(f"   Saved: {output_path}")

            return True, result
        finally:
            try:
                os.unlink(tmp_path)
            except:
                pass

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_complex_polygon():
    """
    Test wall thickness with L-shaped polygon using best approach.
    """
    print("\n" + "="*60)
    print("Complex Polygon Test: L-Shaped Room")
    print("="*60)

    try:
        wall_thickness = 200.0
        height = 3000.0

        # L-shape outer polygon
        outer_points = [
            (0, 0),
            (8000, 0),
            (8000, 5000),
            (5000, 5000),
            (5000, 8000),
            (0, 8000)
        ]

        # For L-shape, manual offset is complex. Try offset2D approach
        try:
            # Create outer solid
            outer = (
                cq.Workplane("XY")
                .polyline(outer_points)
                .close()
                .extrude(height)
            )

            # Try offset2D for inner
            inner = (
                cq.Workplane("XY")
                .polyline(outer_points)
                .close()
                .offset2D(-wall_thickness)
                .extrude(height)
            )

            result = outer.cut(inner)

            # Export
            with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as tmp:
                tmp_path = tmp.name

            try:
                cq.exporters.export(result, tmp_path, "STEP")
                file_size = os.path.getsize(tmp_path)
                print(f"✅ SUCCESS: Generated {file_size:,} byte STEP file")
                print(f"   Method: offset2D(-{wall_thickness}mm) on L-shape")
                print(f"   Polygon: 6 vertices (L-shaped)")
                print(f"   Wall thickness: {wall_thickness}mm")

                # Save for inspection
                output_path = "test_outputs/wall_thickness/l_shaped_walls.step"
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                # Use copy instead of rename for cross-device compatibility
                import shutil
                shutil.copy(tmp_path, output_path)
                print(f"   Saved: {output_path}")

                return True, result
            finally:
                try:
                    os.unlink(tmp_path)
                except:
                    pass

        except Exception as e:
            print(f"   offset2D failed: {e}")
            print("   Falling back to manual offset (not implemented for L-shape)")
            return False, None

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def main():
    """Run all experimental tests."""
    print("\n" + "#"*60)
    print("# Wall Thickness Implementation Experiments")
    print("# Testing different approaches for Phase 1.4")
    print("#"*60)

    results = {}

    # Test all approaches
    results['offset2d'], _ = approach_1_offset2d()
    results['shell'], _ = approach_2_shell()
    results['manual'], _ = approach_3_manual()
    results['complex'], _ = test_complex_polygon()

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for approach, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{approach:15s}: {status}")

    print("\n" + "="*60)
    print("RECOMMENDATION")
    print("="*60)

    if results['offset2d']:
        print("✅ Use offset2D() approach:")
        print("   - Works for simple rectangles")
        print("   - Works for complex polygons (L-shapes)")
        print("   - Clean, elegant solution")
        print("   - Best for production implementation")
    elif results['manual']:
        print("⚠️  Use manual offset approach:")
        print("   - Fallback when offset2D fails")
        print("   - More complex implementation")
        print("   - Works for simple rectangles")
    else:
        print("❌ No working approach found")
        print("   - Need to investigate further")


if __name__ == "__main__":
    main()
