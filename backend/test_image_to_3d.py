"""
Test Image-to-3D generation using Shap-E image300M.

This will download the image300M model (~1.5GB) on first run.
"""
import asyncio
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.triposr import get_triposr_service
from app.services.mesh_converter import get_mesh_converter
from PIL import Image, ImageDraw


def create_test_images() -> dict[str, bytes]:
    """Create simple test images for different objects."""
    test_images = {}

    # 1. Red cube
    img = Image.new('RGB', (256, 256), color='white')
    draw = ImageDraw.Draw(img)
    # Front face
    draw.polygon([(80, 100), (176, 100), (176, 196), (80, 196)], fill='red', outline='black')
    # Top face
    draw.polygon([(80, 100), (128, 60), (224, 60), (176, 100)], fill='#ff6666', outline='black')
    # Right face
    draw.polygon([(176, 100), (224, 60), (224, 156), (176, 196)], fill='#cc0000', outline='black')

    from io import BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    test_images['cube'] = buffer.getvalue()

    # 2. Green sphere
    img2 = Image.new('RGB', (256, 256), color='white')
    draw2 = ImageDraw.Draw(img2)
    draw2.ellipse([64, 64, 192, 192], fill='green', outline='darkgreen')
    # Add shading
    draw2.ellipse([80, 80, 140, 140], fill='lightgreen', outline=None)

    buffer2 = BytesIO()
    img2.save(buffer2, format='PNG')
    test_images['sphere'] = buffer2.getvalue()

    return test_images


async def test_image_to_3d():
    print("=" * 70)
    print("Testing Image-to-3D Generation (Shap-E image300M)")
    print("=" * 70)
    print()

    # Initialize service
    print("1. Initializing image-to-3D service...")
    service = get_triposr_service()

    if not service.enabled:
        print("ERROR: Image-to-3D service not enabled!")
        print("Install Shap-E from: cd docs/useful_projects/shap-e-main && pip install -e .")
        return False

    print(f"   - Service enabled: {service.enabled}")
    print(f"   - Device: {service.device}")
    print(f"   - Using: Shap-E image300M (local, free!)")
    print()

    # Create test images
    print("2. Creating test images...")
    test_images = create_test_images()

    output_dir = Path(__file__).parent / "test_outputs"
    output_dir.mkdir(exist_ok=True)

    # Save test images
    for name, img_bytes in test_images.items():
        img_path = output_dir / f"image_to_3d_input_{name}.png"
        img_path.write_bytes(img_bytes)
        print(f"   - Saved test image: {img_path.name}")
    print()

    # Test generation with cube
    print("3. Generating 3D mesh from image (cube)...")
    print("   - This will download image300M model (~1.5GB) on first run...")
    print("   - Estimated time: 30-60 seconds (GPU) or 2-5 min (CPU)")
    print()

    try:
        cube_bytes = test_images['cube']
        ply_bytes = await service.generate_from_image_async(
            cube_bytes,
            guidance_scale=3.0,
            num_steps=64
        )

        print(f"4. Generation successful!")
        print(f"   - Output size: {len(ply_bytes):,} bytes")
        print(f"   - Format: PLY")
        print()

        # Save PLY output
        ply_path = output_dir / "image_to_3d_cube.ply"
        ply_path.write_bytes(ply_bytes)
        print(f"5. Saved PLY: {ply_path}")
        print()

        # Convert to GLB
        print("6. Converting to GLB format...")
        converter = get_mesh_converter()
        glb_bytes = converter.convert(ply_bytes, "ply", "glb")

        glb_path = output_dir / "image_to_3d_cube.glb"
        glb_path.write_bytes(glb_bytes)
        print(f"   - Saved GLB: {glb_path}")
        print()

        # Test with sphere (faster - 32 steps)
        print("7. Quick test with sphere (32 steps)...")
        sphere_bytes = test_images['sphere']
        sphere_ply = await service.generate_from_image_async(
            sphere_bytes,
            guidance_scale=3.0,
            num_steps=32  # Faster for testing
        )

        sphere_path = output_dir / "image_to_3d_sphere.ply"
        sphere_path.write_bytes(sphere_ply)
        print(f"   - Saved sphere: {sphere_path.name} ({len(sphere_ply):,} bytes)")
        print()

        print("=" * 70)
        print("SUCCESS: Image-to-3D generation is working!")
        print("=" * 70)
        print()
        print("Summary:")
        print(f"  ✅ Shap-E image300M model loaded successfully")
        print(f"  ✅ Image-to-3D generation working (cube + sphere)")
        print(f"  ✅ Format conversion working (PLY → GLB)")
        print(f"  ✅ Output files saved to: {output_dir}")
        print()
        print("Phase 2 Complete! 🎉")
        return True

    except Exception as e:
        print(f"ERROR: Generation failed!")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_image_to_3d())
    sys.exit(0 if success else 1)
