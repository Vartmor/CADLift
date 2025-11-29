#!/usr/bin/env python3
"""
Test suite for Phase 2 improvements.

Tests:
- Phase 2.1: CIRCLE/ARC support and layer filtering (CAD pipeline)
- Phase 2.2: Enhanced preprocessing and line simplification (Image pipeline)
"""

import os
import sys
from pathlib import Path
import tempfile

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))


def test_circle_arc_dxf():
    """Test 2.1: CIRCLE and ARC conversion to polygons"""
    print("\n" + "="*60)
    print("Test 2.1: CIRCLE and ARC Support")
    print("="*60)

    import ezdxf

    # Create a simple DXF with CIRCLE and ARC
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    # Add a CIRCLE (radius 1000mm at origin)
    msp.add_circle(center=(0, 0), radius=1000)

    # Add an ARC (radius 500mm, 0° to 90°)
    msp.add_arc(center=(3000, 0), radius=500, start_angle=0, end_angle=90)

    # Add a rectangle for reference
    msp.add_lwpolyline(
        [(5000, 0), (6000, 0), (6000, 1000), (5000, 1000)],
        close=True
    )

    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False, mode='w') as tmp:
        tmp_path = tmp.name

    try:
        doc.saveas(tmp_path)
        print(f"Created test DXF with CIRCLE, ARC, and LWPOLYLINE")

        # Now test parsing
        from app.pipelines.cad import _generate_model
        from app.models import Job

        # Create mock job
        class MockJob:
            def __init__(self):
                self.id = "test"
                self.params = {}

        job = MockJob()
        model = _generate_model(Path(tmp_path), job)

        print(f"✅ Parsed DXF successfully")
        print(f"   Polygons found: {len(model['polygons'])}")
        print(f"   Expected: 3 (circle + arc + rectangle)")

        # Verify circle has ~36 points
        circle_poly = model['polygons'][0]  # Should be sorted by size
        print(f"   Circle polygon: {len(circle_poly)} vertices")

        if len(model['polygons']) >= 2:
            print(f"   Arc polygon: {len(model['polygons'][1])} vertices")

        if len(model['polygons']) == 3:
            print("✅ All shapes detected correctly")
            return True
        else:
            print(f"⚠️  Expected 3 polygons, got {len(model['polygons'])}")
            return False

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass


def test_layer_filtering():
    """Test 2.1: Layer filtering"""
    print("\n" + "="*60)
    print("Test 2.1: Layer Filtering")
    print("="*60)

    import ezdxf

    # Create DXF with multiple layers
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    # Create layers
    doc.layers.add("WALLS", color=1)
    doc.layers.add("FURNITURE", color=2)
    doc.layers.add("DIMENSIONS", color=3)

    # Add shapes on different layers
    msp.add_lwpolyline(
        [(0, 0), (5000, 0), (5000, 4000), (0, 4000)],
        close=True,
        dxfattribs={"layer": "WALLS"}
    )

    msp.add_lwpolyline(
        [(1000, 1000), (2000, 1000), (2000, 2000), (1000, 2000)],
        close=True,
        dxfattribs={"layer": "FURNITURE"}
    )

    msp.add_lwpolyline(
        [(500, 500), (1000, 500), (1000, 1000), (500, 1000)],
        close=True,
        dxfattribs={"layer": "DIMENSIONS"}
    )

    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False, mode='w') as tmp:
        tmp_path = tmp.name

    try:
        doc.saveas(tmp_path)
        print(f"Created test DXF with 3 layers (WALLS, FURNITURE, DIMENSIONS)")

        # Test 1: Parse all layers
        from app.pipelines.cad import _generate_model
        from app.models import Job

        class MockJob:
            def __init__(self, params=None):
                self.id = "test"
                self.params = params or {}

        job_all = MockJob()
        model_all = _generate_model(Path(tmp_path), job_all)
        print(f"✅ All layers: {len(model_all['polygons'])} polygons")

        # Test 2: Filter for WALLS only
        job_walls = MockJob(params={"layers": "WALLS"})
        model_walls = _generate_model(Path(tmp_path), job_walls)
        print(f"✅ WALLS only: {len(model_walls['polygons'])} polygons (expected: 1)")

        # Test 3: Filter for multiple layers
        job_multi = MockJob(params={"layers": "WALLS,FURNITURE"})
        model_multi = _generate_model(Path(tmp_path), job_multi)
        print(f"✅ WALLS+FURNITURE: {len(model_multi['polygons'])} polygons (expected: 2)")

        if len(model_all['polygons']) == 3 and len(model_walls['polygons']) == 1 and len(model_multi['polygons']) == 2:
            print("✅ Layer filtering works correctly")
            return True
        else:
            print("⚠️  Layer filtering results unexpected")
            return False

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass


def test_image_preprocessing():
    """Test 2.2: Enhanced image preprocessing"""
    print("\n" + "="*60)
    print("Test 2.2: Enhanced Image Preprocessing")
    print("="*60)

    import numpy as np
    import cv2

    # Create a simple test image with a rectangle
    img = np.ones((200, 200), dtype=np.uint8) * 128  # Gray background

    # Draw a filled rectangle
    cv2.rectangle(img, (50, 50), (150, 150), 255, -1)

    # Add some noise
    noise = np.random.normal(0, 10, img.shape).astype(np.uint8)
    img = cv2.add(img, noise)

    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        cv2.imwrite(tmp_path, img)
        print(f"Created test image (200x200 with rectangle)")

        # Test preprocessing
        from app.pipelines.image import _load_image, _preprocess_image, _extract_contours

        # Load and preprocess
        original = _load_image(Path(tmp_path))
        preprocessed = _preprocess_image(original, enhance_contrast=True)

        print(f"✅ Preprocessing applied (CLAHE + bilateral filter)")
        print(f"   Original shape: {original.shape}")
        print(f"   Preprocessed shape: {preprocessed.shape}")

        # Test contour extraction with and without preprocessing
        contours_basic = _extract_contours(
            original,
            canny_threshold1=50,
            canny_threshold2=150,
            blur_kernel=5,
            min_contour_area=100,
            enhance_preprocessing=False
        )

        contours_enhanced = _extract_contours(
            original,
            canny_threshold1=50,
            canny_threshold2=150,
            blur_kernel=5,
            min_contour_area=100,
            enhance_preprocessing=True
        )

        print(f"✅ Basic extraction: {len(contours_basic)} contours")
        print(f"✅ Enhanced extraction: {len(contours_enhanced)} contours")

        if len(contours_enhanced) > 0:
            print("✅ Contour detection works with preprocessing")
            return True
        else:
            print("⚠️  No contours detected")
            return False

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass


def test_douglas_peucker_simplification():
    """Test 2.2: Douglas-Peucker line simplification"""
    print("\n" + "="*60)
    print("Test 2.2: Douglas-Peucker Line Simplification")
    print("="*60)

    import numpy as np
    import cv2

    # Create test image with a closed wavy shape
    img = np.zeros((300, 300), dtype=np.uint8)

    # Draw a filled wavy circle/blob
    import math
    pts = []
    for i in range(72):  # 72 points = 5° per point
        angle = 2 * math.pi * i / 72
        # Radius varies (creates wavy circle)
        radius = 80 + 15 * math.sin(8 * angle)
        x = int(150 + radius * math.cos(angle))
        y = int(150 + radius * math.sin(angle))
        pts.append((x, y))

    # Draw filled polygon
    pts_array = np.array(pts, dtype=np.int32)
    cv2.fillPoly(img, [pts_array], 255)

    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        cv2.imwrite(tmp_path, img)
        print(f"Created test image with wavy circular shape (72 points)")

        from app.pipelines.image import _load_image, _extract_contours

        original = _load_image(Path(tmp_path))

        # Test with different epsilon values
        contours_fine = _extract_contours(
            original,
            canny_threshold1=50,
            canny_threshold2=150,
            blur_kernel=3,
            min_contour_area=10,
            simplify_epsilon=0.001,  # Very detailed
            enhance_preprocessing=False
        )

        contours_coarse = _extract_contours(
            original,
            canny_threshold1=50,
            canny_threshold2=150,
            blur_kernel=3,
            min_contour_area=10,
            simplify_epsilon=0.05,  # More simplified
            enhance_preprocessing=False
        )

        if contours_fine and contours_coarse:
            fine_points = len(contours_fine[0])
            coarse_points = len(contours_coarse[0])

            print(f"✅ Fine simplification (ε=0.001): {fine_points} points")
            print(f"✅ Coarse simplification (ε=0.05): {coarse_points} points")

            if coarse_points < fine_points:
                print(f"✅ Douglas-Peucker simplification working correctly")
                print(f"   Reduction: {100*(1-coarse_points/fine_points):.1f}%")
                return True
            else:
                print("⚠️  Simplification didn't reduce points as expected")
                return False
        else:
            print("⚠️  No contours detected")
            return False

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass


def main():
    """Run all Phase 2 tests"""
    print("\n" + "#"*60)
    print("# Phase 2 Improvements Test Suite")
    print("# Phase 2.1: CAD Pipeline + Phase 2.2: Image Pipeline")
    print("#"*60)

    results = {
        "circle_arc": test_circle_arc_dxf(),
        "layer_filtering": test_layer_filtering(),
        "image_preprocessing": test_image_preprocessing(),
        "douglas_peucker": test_douglas_peucker_simplification(),
    }

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    passed = sum(1 for success in results.values() if success)
    total = len(results)

    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:25s}: {status}")

    print("\n" + "="*60)
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("="*60)
        print("\nPhase 2.1 and 2.2 implementations verified!")
        return 0
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total})")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
