"""
Test Shap-E model loading and generation.

This will download ~4GB of models on first run (auto-cached for future use).
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.shap_e import ShapEService


async def test_generation():
    print("=" * 60)
    print("Testing Shap-E Local Model Loading & Generation")
    print("=" * 60)
    print()

    # Initialize service
    print("1. Initializing Shap-E service...")
    service = ShapEService()

    if not service.enabled:
        print("ERROR: Shap-E service not enabled!")
        return False

    print(f"   - Service enabled: {service.enabled}")
    print(f"   - Device: {service.device}")
    print()

    # Test generation
    print("2. Generating test object: 'a simple cube'")
    print("   - This will download models (~4GB) on first run...")
    print("   - Estimated time: 30-60 seconds (GPU) or 2-5 min (CPU)")
    print()

    try:
        ply_bytes = await service.generate_from_text(
            prompt="a simple cube",
            guidance_scale=15.0,
            num_steps=64
        )

        print(f"3. Generation successful!")
        print(f"   - Output size: {len(ply_bytes):,} bytes")
        print(f"   - Format: PLY (Point cloud/mesh)")
        print()

        # Save output
        output_path = Path(__file__).parent / "test_output_cube.ply"
        output_path.write_bytes(ply_bytes)
        print(f"4. Saved to: {output_path}")
        print()

        print("=" * 60)
        print("SUCCESS: Shap-E is working correctly!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"ERROR: Generation failed!")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_generation())
    sys.exit(0 if success else 1)
