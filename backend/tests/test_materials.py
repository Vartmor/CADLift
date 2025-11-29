"""
Tests for material library and export functionality (Phase 6.4).

Tests material definitions, OBJ+MTL export, and glTF PBR materials.
"""

import tempfile
from pathlib import Path
import json

from app.materials import (
    MATERIAL_LIBRARY,
    get_material_for_layer,
    generate_mtl_content,
    generate_gltf_materials
)
from app.pipelines.geometry import (
    export_obj_with_mtl,
    export_gltf_with_materials
)


def test_material_library():
    """Test that material library has expected materials."""
    # Verify core materials exist
    assert "concrete" in MATERIAL_LIBRARY
    assert "glass" in MATERIAL_LIBRARY
    assert "wood" in MATERIAL_LIBRARY
    assert "metal" in MATERIAL_LIBRARY
    assert "steel" in MATERIAL_LIBRARY

    # Verify material properties
    concrete = MATERIAL_LIBRARY["concrete"]
    assert "color" in concrete
    assert "roughness" in concrete
    assert "metallic" in concrete
    assert "transparency" in concrete
    assert "dxf_color" in concrete

    # Verify color is RGB tuple
    assert len(concrete["color"]) == 3
    assert all(0.0 <= c <= 1.0 for c in concrete["color"])

    # Verify roughness and metallic are in valid range
    assert 0.0 <= concrete["roughness"] <= 1.0
    assert 0.0 <= concrete["metallic"] <= 1.0

    print(f"✓ Material library has {len(MATERIAL_LIBRARY)} materials")


def test_layer_to_material_mapping():
    """Test layer name to material mapping."""
    # Test direct matches
    assert get_material_for_layer("WALLS") == "concrete"
    assert get_material_for_layer("WINDOW") == "glass"
    assert get_material_for_layer("DOOR") == "wood"
    assert get_material_for_layer("BEAM") == "steel"

    # Test case insensitivity
    assert get_material_for_layer("walls") == "concrete"
    assert get_material_for_layer("Windows") == "glass"

    # Test partial matches
    assert get_material_for_layer("FLOOR-1-WALLS") == "concrete"
    assert get_material_for_layer("FLOOR-2-WINDOW") == "glass"

    # Test default
    assert get_material_for_layer("UNKNOWN_LAYER") == "concrete"
    assert get_material_for_layer("") == "concrete"
    assert get_material_for_layer(None) == "concrete"

    print("✓ Layer to material mapping works correctly")


def test_mtl_generation():
    """Test MTL file generation."""
    materials_used = {"concrete", "glass", "wood"}

    mtl_content = generate_mtl_content(materials_used)

    # Verify MTL structure
    assert "newmtl concrete" in mtl_content
    assert "newmtl glass" in mtl_content
    assert "newmtl wood" in mtl_content

    # Verify MTL properties
    assert "Ka " in mtl_content  # Ambient
    assert "Kd " in mtl_content  # Diffuse
    assert "Ks " in mtl_content  # Specular
    assert "Ns " in mtl_content  # Shininess
    assert "illum " in mtl_content  # Illumination model

    # Verify transparency for glass
    assert "d " in mtl_content  # Dissolve

    print(f"✓ Generated MTL file: {len(mtl_content)} bytes")
    print(f"✓ MTL preview:\n{mtl_content[:500]}...")


def test_gltf_material_generation():
    """Test glTF PBR material generation."""
    materials_used = {"concrete", "glass", "metal"}

    gltf_materials = generate_gltf_materials(materials_used)

    # Verify structure
    assert isinstance(gltf_materials, list)
    assert len(gltf_materials) == 3

    # Verify first material (concrete)
    concrete_mat = next(m for m in gltf_materials if m["name"] == "concrete")
    assert "pbrMetallicRoughness" in concrete_mat
    assert "baseColorFactor" in concrete_mat["pbrMetallicRoughness"]
    assert "metallicFactor" in concrete_mat["pbrMetallicRoughness"]
    assert "roughnessFactor" in concrete_mat["pbrMetallicRoughness"]

    # Verify baseColorFactor is RGBA
    base_color = concrete_mat["pbrMetallicRoughness"]["baseColorFactor"]
    assert len(base_color) == 4
    assert all(0.0 <= c <= 1.0 for c in base_color)

    # Verify glass transparency
    glass_mat = next(m for m in gltf_materials if m["name"] == "glass")
    assert "alphaMode" in glass_mat
    assert glass_mat["alphaMode"] in ["BLEND", "MASK"]

    # Verify metal properties
    metal_mat = next(m for m in gltf_materials if m["name"] == "metal")
    assert metal_mat["pbrMetallicRoughness"]["metallicFactor"] > 0.5

    print(f"✓ Generated {len(gltf_materials)} glTF materials")
    print(f"✓ Sample material: {json.dumps(concrete_mat, indent=2)}")


def test_obj_mtl_export():
    """Test OBJ+MTL export with materials."""
    # Create simple room
    room_polygon = [[0.0, 0.0], [5000.0, 0.0], [5000.0, 4000.0], [0.0, 4000.0]]

    # Export with concrete material
    obj_bytes, mtl_bytes = export_obj_with_mtl(
        [room_polygon],
        height=3000.0,
        wall_thickness=200.0,
        material="concrete"
    )

    # Verify OBJ was generated
    assert len(obj_bytes) > 500, "OBJ file too small"
    obj_content = obj_bytes.decode('utf-8')
    assert "mtllib model.mtl" in obj_content, "Missing MTL library reference"
    assert "usemtl concrete" in obj_content, "Missing material usage"
    assert "v " in obj_content, "Missing vertices"
    assert "f " in obj_content, "Missing faces"

    # Verify MTL was generated
    assert len(mtl_bytes) > 100, "MTL file too small"
    mtl_content = mtl_bytes.decode('utf-8')
    assert "newmtl concrete" in mtl_content, "Missing concrete material definition"

    print(f"✓ Exported OBJ+MTL: OBJ={len(obj_bytes)} bytes, MTL={len(mtl_bytes)} bytes")

    # Save test outputs
    output_path = Path("test_outputs") / "materials"
    output_path.mkdir(parents=True, exist_ok=True)

    with open(output_path / "room_concrete.obj", "wb") as f:
        f.write(obj_bytes)

    with open(output_path / "room_concrete.mtl", "wb") as f:
        f.write(mtl_bytes)

    print(f"✓ Saved test outputs to {output_path}")


def test_gltf_with_materials():
    """Test glTF export with PBR materials."""
    # Create simple room
    room_polygon = [[0.0, 0.0], [5000.0, 0.0], [5000.0, 4000.0], [0.0, 4000.0]]

    # Export with glass material
    gltf_bytes = export_gltf_with_materials(
        [room_polygon],
        height=3000.0,
        wall_thickness=200.0,
        material="glass",
        binary=False  # Export as JSON for inspection
    )

    # Verify glTF was generated
    assert len(gltf_bytes) > 1000, "glTF file too small"

    # Parse and verify structure
    gltf_json = json.loads(gltf_bytes.decode('utf-8'))

    assert "materials" in gltf_json, "Missing materials"
    assert len(gltf_json["materials"]) > 0, "No materials defined"

    # Verify glass material exists
    glass_mat = next((m for m in gltf_json["materials"] if m["name"] == "glass"), None)
    assert glass_mat is not None, "Glass material not found"
    assert "pbrMetallicRoughness" in glass_mat

    print(f"✓ Exported glTF with materials: {len(gltf_bytes)} bytes")
    print(f"✓ Materials: {[m['name'] for m in gltf_json['materials']]}")

    # Save test output
    output_path = Path("test_outputs") / "materials"
    output_path.mkdir(parents=True, exist_ok=True)

    with open(output_path / "room_glass.gltf", "wb") as f:
        f.write(gltf_bytes)

    print(f"✓ Saved test output to {output_path}")


def test_glb_binary_export():
    """Test GLB binary export with materials."""
    # Create simple room
    room_polygon = [[0.0, 0.0], [5000.0, 0.0], [5000.0, 4000.0], [0.0, 4000.0]]

    # Export as GLB (binary)
    glb_bytes = export_gltf_with_materials(
        [room_polygon],
        height=3000.0,
        wall_thickness=200.0,
        material="wood",
        binary=True
    )

    # Verify GLB was generated
    assert len(glb_bytes) > 1000, "GLB file too small"

    # GLB files start with "glTF" magic number
    assert glb_bytes[:4] == b"glTF", "Not a valid GLB file"

    print(f"✓ Exported GLB binary: {len(glb_bytes)} bytes")

    # Save test output
    output_path = Path("test_outputs") / "materials"
    output_path.mkdir(parents=True, exist_ok=True)

    with open(output_path / "room_wood.glb", "wb") as f:
        f.write(glb_bytes)

    print(f"✓ Saved test output to {output_path}")


if __name__ == "__main__":
    print("Testing material library and export functionality (Phase 6.4)")
    print("=" * 60)

    print("\n1. Testing material library...")
    test_material_library()

    print("\n2. Testing layer to material mapping...")
    test_layer_to_material_mapping()

    print("\n3. Testing MTL generation...")
    test_mtl_generation()

    print("\n4. Testing glTF material generation...")
    test_gltf_material_generation()

    print("\n5. Testing OBJ+MTL export...")
    test_obj_mtl_export()

    print("\n6. Testing glTF export with materials...")
    test_gltf_with_materials()

    print("\n7. Testing GLB binary export...")
    test_glb_binary_export()

    print("\n" + "=" * 60)
    print("✓ All material tests passed!")
