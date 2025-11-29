"""
Test TripoSR image-to-3D generation.

This will download the TripoSR model (~2-3GB) on first run.
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.triposr import get_triposr_service
from PIL import Image, ImageDraw


def create_test_image() -> bytes:
    """Create a simple test image (red cube)."""
    # Create a 256x256 image with a red cube
    img = Image.new('RGB', (256, 256), color='white')
    draw = ImageDraw.Draw(img)

    # Draw a simple cube-like shape
    # Front face (red)
    draw.polygon([
        (80, 100), (176, 100), (176, 196), (80, 196)
    ], fill='red', outline='black')

    # Top face (lighter red)
    draw.polygon([
        (80, 100), (128, 60), (224, 60), (176, 100)
    ], fill='#ff6666', outline='black')

    # Right face (darker red)
    draw.polygon([
        (176, 100), (224, 60), (224, 156), (176, 196)
    ], fill='#cc0000', outline='black')

    # Convert to bytes
    from io import BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def test_triposr():
    print("=" * 60)
    print("Testing TripoSR Image-to-3D Generation")
    print("=" * 60)
    print()

    # Initialize service
    print("1. Initializing TripoSR service...")
    service = get_triposr_service()

    if not service.enabled:
        print("ERROR: TripoSR service not enabled!")
        print("Install with: pip install transformers pillow")
        return False

    print(f"   - Service enabled: {service.enabled}")
    print(f"   - Device: {service.device}")
    print()

    # Create test image
    print("2. Creating test image (simple cube)...")
    test_image_bytes = create_test_image()

    # Save test image
    test_image_path = Path(__file__).parent / "test_outputs" / "triposr_test_input.png"
    test_image_path.parent.mkdir(exist_ok=True)
    test_image_path.write_bytes(test_image_bytes)
    print(f"   - Saved test image: {test_image_path}")
    print()

    # Test generation
    print("3. Generating 3D mesh from image...")
    print("   - This will download TripoSR model (~2-3GB) on first run...")
    print("   - Estimated time: 10-60 seconds (GPU) or 2-3 min (CPU)")
    print()

    try:
        obj_bytes = service.generate_from_image(test_image_bytes)

        print(f"4. Generation successful!")
        print(f"   - Output size: {len(obj_bytes):,} bytes")
        print(f"   - Format: OBJ (Wavefront)")
        print()

        # Save output
        output_path = Path(__file__).parent / "test_outputs" / "triposr_test_cube.obj"
        output_path.write_bytes(obj_bytes)
        print(f"5. Saved to: {output_path}")
        print()

        print("=" * 60)
        print("SUCCESS: TripoSR is working correctly!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"ERROR: Generation failed!")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_triposr()
    sys.exit(0 if success else 1)
