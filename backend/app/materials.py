"""
Material library and definitions for Phase 6.4 (Materials & Appearance).

Provides material definitions for CAD/3D export formats including:
- OBJ+MTL (Wavefront materials)
- glTF/GLB (PBR materials)
- DXF color coding
"""

from typing import TypedDict


class MaterialProperties(TypedDict):
    """Material properties for rendering."""
    name: str
    # Base color (RGB, 0-1 range)
    color: tuple[float, float, float]
    # PBR properties
    roughness: float  # 0.0 = smooth/glossy, 1.0 = rough/matte
    metallic: float   # 0.0 = dielectric, 1.0 = metal
    # Optional properties
    transparency: float  # 0.0 = opaque, 1.0 = fully transparent
    # DXF AutoCAD Color Index
    dxf_color: int


# Material library with physically-based properties
MATERIAL_LIBRARY: dict[str, MaterialProperties] = {
    "concrete": {
        "name": "Concrete",
        "color": (0.7, 0.7, 0.7),
        "roughness": 0.8,
        "metallic": 0.0,
        "transparency": 0.0,
        "dxf_color": 8  # Gray
    },
    "brick": {
        "name": "Brick",
        "color": (0.7, 0.3, 0.2),
        "roughness": 0.85,
        "metallic": 0.0,
        "transparency": 0.0,
        "dxf_color": 10  # Red
    },
    "glass": {
        "name": "Glass",
        "color": (0.8, 0.9, 1.0),
        "roughness": 0.1,
        "metallic": 0.0,
        "transparency": 0.9,
        "dxf_color": 4  # Cyan
    },
    "wood": {
        "name": "Wood",
        "color": (0.6, 0.4, 0.2),
        "roughness": 0.6,
        "metallic": 0.0,
        "transparency": 0.0,
        "dxf_color": 30  # Brown
    },
    "metal": {
        "name": "Metal",
        "color": (0.8, 0.8, 0.8),
        "roughness": 0.3,
        "metallic": 1.0,
        "transparency": 0.0,
        "dxf_color": 7  # White/Light gray
    },
    "steel": {
        "name": "Steel",
        "color": (0.5, 0.5, 0.6),
        "roughness": 0.4,
        "metallic": 1.0,
        "transparency": 0.0,
        "dxf_color": 252  # Gray
    },
    "aluminum": {
        "name": "Aluminum",
        "color": (0.85, 0.85, 0.88),
        "roughness": 0.2,
        "metallic": 1.0,
        "transparency": 0.0,
        "dxf_color": 7  # White
    },
    "copper": {
        "name": "Copper",
        "color": (0.95, 0.64, 0.54),
        "roughness": 0.35,
        "metallic": 1.0,
        "transparency": 0.0,
        "dxf_color": 40  # Orange/copper
    },
    "plastic": {
        "name": "Plastic",
        "color": (0.9, 0.9, 0.9),
        "roughness": 0.5,
        "metallic": 0.0,
        "transparency": 0.0,
        "dxf_color": 7  # White
    },
    "tile": {
        "name": "Tile",
        "color": (0.95, 0.95, 0.95),
        "roughness": 0.2,
        "metallic": 0.0,
        "transparency": 0.0,
        "dxf_color": 7  # White
    },
    "carpet": {
        "name": "Carpet",
        "color": (0.6, 0.5, 0.4),
        "roughness": 0.9,
        "metallic": 0.0,
        "transparency": 0.0,
        "dxf_color": 36  # Tan/beige
    },
    "paint": {
        "name": "Paint",
        "color": (0.95, 0.95, 0.95),
        "roughness": 0.6,
        "metallic": 0.0,
        "transparency": 0.0,
        "dxf_color": 7  # White
    }
}


# Layer name to material mapping
LAYER_MATERIAL_MAP: dict[str, str] = {
    # Walls
    "WALLS": "concrete",
    "WALL": "concrete",
    "WALL-CONCRETE": "concrete",
    "WALL-BRICK": "brick",
    "WALL-WOOD": "wood",
    "EXTERIOR": "concrete",
    "INTERIOR": "paint",

    # Windows
    "WINDOW": "glass",
    "WINDOWS": "glass",
    "WIN": "glass",
    "GLASS": "glass",
    "GLAZING": "glass",

    # Doors
    "DOOR": "wood",
    "DOORS": "wood",
    "ENTRANCE": "wood",

    # Floors/Ceilings
    "FLOOR": "tile",
    "FLOORS": "tile",
    "CEILING": "paint",
    "CEILINGS": "paint",
    "SLAB": "concrete",

    # Structural
    "BEAM": "steel",
    "BEAMS": "steel",
    "COLUMN": "steel",
    "COLUMNS": "steel",
    "FRAME": "metal",
    "STRUCTURE": "steel",

    # Finishes
    "TILE": "tile",
    "CARPET": "carpet",
    "WOOD-FLOOR": "wood",

    # Default
    "0": "concrete",  # DXF layer 0
    "FOOTPRINT": "concrete",
}


def get_material_for_layer(layer_name: str) -> str:
    """
    Get material name for a given DXF layer.

    Args:
        layer_name: DXF layer name

    Returns:
        Material name (key in MATERIAL_LIBRARY), defaults to "concrete"
    """
    if not layer_name:
        return "concrete"

    layer_upper = layer_name.upper()

    # Direct match
    if layer_upper in LAYER_MATERIAL_MAP:
        return LAYER_MATERIAL_MAP[layer_upper]

    # Partial match (e.g., "FLOOR-1-WALLS" -> "WALLS")
    for layer_pattern, material in LAYER_MATERIAL_MAP.items():
        if layer_pattern in layer_upper:
            return material

    # Default
    return "concrete"


def generate_mtl_content(materials_used: set[str]) -> str:
    """
    Generate Wavefront MTL file content for specified materials.

    Args:
        materials_used: Set of material names to include

    Returns:
        MTL file content as string
    """
    mtl_lines = ["# CADLift Material Library (Phase 6.4)", "# Generated MTL file for Wavefront OBJ", ""]

    for material_name in sorted(materials_used):
        if material_name not in MATERIAL_LIBRARY:
            continue

        mat = MATERIAL_LIBRARY[material_name]

        mtl_lines.append(f"newmtl {material_name}")
        mtl_lines.append(f"# {mat['name']}")

        # Ambient color (Ka)
        mtl_lines.append(f"Ka {mat['color'][0]:.3f} {mat['color'][1]:.3f} {mat['color'][2]:.3f}")

        # Diffuse color (Kd) - main color
        mtl_lines.append(f"Kd {mat['color'][0]:.3f} {mat['color'][1]:.3f} {mat['color'][2]:.3f}")

        # Specular color (Ks) - based on roughness
        specular_intensity = 1.0 - mat['roughness']
        mtl_lines.append(f"Ks {specular_intensity:.3f} {specular_intensity:.3f} {specular_intensity:.3f}")

        # Specular exponent (Ns) - shininess (0-1000, higher = shinier)
        shininess = (1.0 - mat['roughness']) * 200
        mtl_lines.append(f"Ns {shininess:.1f}")

        # Transparency (d = dissolve, 1.0 = opaque, 0.0 = transparent)
        dissolve = 1.0 - mat['transparency']
        if mat['transparency'] > 0:
            mtl_lines.append(f"d {dissolve:.3f}")
            mtl_lines.append(f"Tr {mat['transparency']:.3f}")

        # Illumination model
        # 0 = color, 1 = ambient + diffuse, 2 = highlight, 4 = glass, 7 = reflection + refraction
        if mat['transparency'] > 0.5:
            mtl_lines.append("illum 4")  # Glass/transparent
        elif mat['metallic'] > 0.5:
            mtl_lines.append("illum 3")  # Reflection
        else:
            mtl_lines.append("illum 2")  # Highlight

        mtl_lines.append("")  # Blank line between materials

    return "\n".join(mtl_lines)


def generate_gltf_materials(materials_used: set[str]) -> list[dict]:
    """
    Generate glTF PBR material definitions for specified materials.

    Args:
        materials_used: Set of material names to include

    Returns:
        List of glTF material dicts
    """
    gltf_materials = []

    for material_name in sorted(materials_used):
        if material_name not in MATERIAL_LIBRARY:
            continue

        mat = MATERIAL_LIBRARY[material_name]

        # glTF PBR metallic-roughness material
        material_def = {
            "name": material_name,
            "pbrMetallicRoughness": {
                "baseColorFactor": [
                    mat['color'][0],
                    mat['color'][1],
                    mat['color'][2],
                    1.0 - mat['transparency']  # Alpha channel
                ],
                "metallicFactor": mat['metallic'],
                "roughnessFactor": mat['roughness']
            }
        }

        # Add alpha mode for transparent materials
        if mat['transparency'] > 0.01:
            material_def["alphaMode"] = "BLEND" if mat['transparency'] < 0.99 else "MASK"
            if material_def["alphaMode"] == "MASK":
                material_def["alphaCutoff"] = 0.5

        # Double-sided for transparent materials
        if mat['transparency'] > 0.01:
            material_def["doubleSided"] = True

        gltf_materials.append(material_def)

    return gltf_materials
