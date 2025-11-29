"""
Test DXF export fix.

This tests the bug fix for DXF export (temp file approach).
"""
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.mesh_converter import get_mesh_converter


def test_dxf_export():
    print("=" * 60)
    print("Testing DXF Export Fix")
    print("=" * 60)
    print()

    # Create simple test mesh (cube)
    print("1. Creating test GLB mesh...")
    import trimesh

    # Create a simple cube mesh
    cube = trimesh.creation.box(extents=[1, 1, 1])

    # Export to GLB
    glb_bytes = cube.export(file_type='glb')
    print(f"   - Created cube mesh: {len(glb_bytes):,} bytes")
    print()

    # Test DXF conversion
    print("2. Testing DXF export (previously broken)...")
    converter = get_mesh_converter()

    try:
        dxf_bytes = converter.convert(glb_bytes, "glb", "dxf")

        print(f"3. DXF export successful!")
        print(f"   - Output size: {len(dxf_bytes):,} bytes")
        print()

        # Save output for verification
        output_dir = Path(__file__).parent / "test_outputs"
        output_dir.mkdir(exist_ok=True)

        dxf_path = output_dir / "dxf_export_test.dxf"
        dxf_path.write_bytes(dxf_bytes)
        print(f"4. Saved DXF: {dxf_path}")
        print()

        # Verify it's a valid DXF file (should contain "0\nSECTION")
        dxf_text = dxf_bytes.decode('utf-8')
        # DXF files may have leading whitespace/indentation
        if 'SECTION' in dxf_text and 'HEADER' in dxf_text:
            print("5. DXF file format validation: ✅ PASSED")
            print(f"   - File contains SECTION and HEADER markers")
            print()
            print("=" * 60)
            print("SUCCESS: DXF export bug is FIXED!")
            print("=" * 60)
            return True
        else:
            print("5. DXF file format validation: ❌ FAILED")
            print(f"   - File starts with: {dxf_text[:50]}")
            return False

    except Exception as e:
        print(f"ERROR: DXF export failed!")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_dxf_export()
    sys.exit(0 if success else 1)
