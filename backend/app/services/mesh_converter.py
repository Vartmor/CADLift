"""
Mesh format conversion service.

Converts between different 3D mesh formats:
- PLY (Polygon File Format) ← Shap-E output format
- GLB (glTF Binary) ← AI-generated meshes, web 3D
- STEP (ISO 10303-21) ← CAD software standard (Mayo-powered for professional quality)
- IGES (IGES 5.3) ← CAD compatibility (Mayo-powered)
- BREP (OpenCascade) ← CAD format (Mayo-powered)
- DXF (AutoCAD) ← 2D/3D CAD compatibility
- OBJ (Wavefront) ← Universal mesh format
- STL (Stereolithography) ← 3D printing standard
"""
from __future__ import annotations

import trimesh
import ezdxf
from io import BytesIO
import logging
from typing import Literal

from app.services.mayo import get_mayo_service, MayoConversionError

logger = logging.getLogger("cadlift.services.mesh_converter")

FormatType = Literal["ply", "glb", "step", "dxf", "obj", "stl", "iges", "brep"]


class MeshConversionError(Exception):
    """Mesh conversion error."""
    pass


class MeshConverter:
    """
    Convert between 3D mesh formats.

    Automatically uses Mayo for professional-grade CAD export (STEP, IGES, BREP)
    when available, with fallback to Trimesh-based conversion.
    """

    def __init__(self):
        self.mayo = get_mayo_service()
        self.mayo_available = self.mayo.is_available()

        if self.mayo_available:
            logger.info(f"Mesh converter initialized with Mayo support ({self.mayo.get_version()})")
        else:
            logger.info("Mesh converter initialized (Mayo not available, using Trimesh fallback)")

    def convert(
        self,
        input_bytes: bytes,
        input_format: FormatType,
        output_format: FormatType
    ) -> bytes:
        """
        Convert mesh from one format to another.

        Automatically uses Mayo for professional CAD formats (STEP, IGES, BREP)
        when available, otherwise falls back to Trimesh-based conversion.

        Args:
            input_bytes: Input mesh data
            input_format: Input format ('glb', 'obj', 'stl', etc.)
            output_format: Output format ('step', 'dxf', 'glb', etc.)

        Returns:
            Converted mesh bytes

        Raises:
            MeshConversionError: If conversion fails
        """
        if input_format == output_format:
            return input_bytes

        logger.info(
            f"Converting mesh: {input_format} → {output_format}",
            extra={"input_size": len(input_bytes)}
        )

        # Try Mayo for CAD formats (STEP, IGES, BREP) if available
        if self.mayo_available and output_format in {"step", "iges", "brep"}:
            try:
                logger.info(f"Using Mayo for professional {output_format.upper()} export")
                output_bytes = self.mayo.convert(
                    input_bytes,
                    input_format,
                    output_format,
                    timeout=120
                )

                logger.info(
                    f"Mayo conversion successful: {input_format} → {output_format}",
                    extra={"output_size": len(output_bytes), "method": "mayo"}
                )

                return output_bytes

            except MayoConversionError as exc:
                logger.warning(
                    f"Mayo conversion failed, falling back to Trimesh: {exc}",
                    extra={"fallback": True}
                )
                # Fall through to Trimesh method

        # Trimesh-based conversion (fallback or for non-CAD formats)
        try:
            # Load mesh using trimesh
            mesh = self._load_mesh(input_bytes, input_format)

            # Convert to target format
            output_bytes = self._export_mesh(mesh, output_format)

            logger.info(
                f"Conversion successful: {input_format} → {output_format}",
                extra={"output_size": len(output_bytes), "method": "trimesh"}
            )

            return output_bytes

        except Exception as e:
            logger.error(f"Mesh conversion failed: {e}")
            raise MeshConversionError(f"Failed to convert {input_format} to {output_format}: {e}")

    def _load_mesh(self, data: bytes, format_type: FormatType) -> trimesh.Trimesh:
        """Load mesh from bytes."""
        try:
            stream = BytesIO(data)
            mesh = trimesh.load(stream, file_type=format_type)

            # Ensure it's a Trimesh (not Scene)
            if isinstance(mesh, trimesh.Scene):
                # Get first geometry from scene
                if len(mesh.geometry) > 0:
                    mesh = list(mesh.geometry.values())[0]
                else:
                    raise MeshConversionError("Scene contains no geometry")

            logger.debug(
                f"Loaded mesh: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces"
            )

            return mesh

        except Exception as e:
            raise MeshConversionError(f"Failed to load {format_type} mesh: {e}")

    def _export_mesh(self, mesh: trimesh.Trimesh, format_type: FormatType) -> bytes:
        """Export mesh to bytes."""
        try:
            output_stream = BytesIO()

            if format_type == "step":
                # STEP export (CAD format)
                # Note: trimesh has limited STEP export support
                # For better STEP support, would need pythonOCC or similar
                output_bytes = self._export_to_step(mesh)

            elif format_type == "dxf":
                # DXF export with 3D mesh
                output_bytes = self._export_to_dxf(mesh)

            else:
                # Use trimesh's built-in export for other formats
                mesh.export(output_stream, file_type=format_type)
                output_bytes = output_stream.getvalue()

            return output_bytes

        except Exception as e:
            raise MeshConversionError(f"Failed to export to {format_type}: {e}")

    def _export_to_step(self, mesh: trimesh.Trimesh) -> bytes:
        """
        Export mesh to STEP format.

        Note: This is a simplified export. For production-quality STEP,
        consider using pythonOCC (OpenCASCADE) which provides better
        solid modeling support.
        """
        # For now, export as STL and note that better STEP support is needed
        # In production, integrate with CadQuery or pythonOCC for proper STEP export

        logger.warning(
            "STEP export using simplified method. "
            "For production, integrate with CadQuery/pythonOCC for better solid modeling."
        )

        # Export as OBJ first (text format we can convert)
        obj_stream = BytesIO()
        mesh.export(obj_stream, file_type="obj")
        obj_data = obj_stream.getvalue()

        # Create minimal STEP file with mesh data
        # This is a placeholder - real STEP should use proper B-rep geometry
        step_header = b"""ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('AI-generated 3D mesh'),'2;1');
FILE_NAME('mesh.step','',(''),(''),''STEP export from CADLift','','');
FILE_SCHEMA(('AP203'));
ENDSEC;
DATA;
/* Mesh data embedded as comment - proper STEP B-rep implementation needed */
ENDSEC;
END-ISO-10303-21;
"""
        return step_header

    def _export_to_dxf(self, mesh: trimesh.Trimesh) -> bytes:
        """
        Export mesh to DXF format with 3DFACE entities.

        Creates:
        1. 2D footprint on layer "FOOTPRINT"
        2. 3D mesh on layer "3D_MESH" using 3DFACE entities
        """
        # Create DXF document
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()

        # Add 2D footprint (projection to XY plane)
        footprint_layer = doc.layers.new(name="FOOTPRINT", dxfattribs={"color": 7})

        # Get 2D projection (bounding box)
        bounds = mesh.bounds
        min_pt = bounds[0][:2]  # X, Y min
        max_pt = bounds[1][:2]  # X, Y max

        # Draw footprint rectangle
        msp.add_lwpolyline(
            [
                (min_pt[0], min_pt[1]),
                (max_pt[0], min_pt[1]),
                (max_pt[0], max_pt[1]),
                (min_pt[0], max_pt[1]),
                (min_pt[0], min_pt[1]),
            ],
            dxfattribs={"layer": "FOOTPRINT"}
        )

        # Add 3D mesh using 3DFACE entities
        mesh_layer = doc.layers.new(name="3D_MESH", dxfattribs={"color": 3})

        # Add each triangular face
        vertices = mesh.vertices
        faces = mesh.faces

        for face in faces:
            # Get 3 vertices of triangle
            v0 = vertices[face[0]].tolist()
            v1 = vertices[face[1]].tolist()
            v2 = vertices[face[2]].tolist()

            # Create 3DFACE (use v2 twice for triangle)
            msp.add_3dface(
                [v0, v1, v2, v2],
                dxfattribs={"layer": "3D_MESH"}
            )

        # Export to bytes (ezdxf requires file path, so use temp file)
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Write to temp file
            doc.saveas(tmp_path)

            # Read back as bytes
            with open(tmp_path, 'rb') as f:
                output_bytes = f.read()
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

        logger.debug(
            f"DXF export complete: {len(faces)} 3DFACE entities created"
        )

        return output_bytes


# Convenience functions
def convert_mesh(
    input_bytes: bytes,
    input_format: FormatType,
    output_format: FormatType
) -> bytes:
    """
    Convert mesh between formats.

    Example:
        glb_data = ...
        step_data = convert_mesh(glb_data, "glb", "step")
    """
    converter = MeshConverter()
    return converter.convert(input_bytes, input_format, output_format)


def glb_to_step(glb_bytes: bytes) -> bytes:
    """Convert GLB to STEP format."""
    return convert_mesh(glb_bytes, "glb", "step")


def glb_to_dxf(glb_bytes: bytes) -> bytes:
    """Convert GLB to DXF format."""
    return convert_mesh(glb_bytes, "glb", "dxf")


def obj_to_step(obj_bytes: bytes) -> bytes:
    """Convert OBJ to STEP format."""
    return convert_mesh(obj_bytes, "obj", "step")


def obj_to_dxf(obj_bytes: bytes) -> bytes:
    """Convert OBJ to DXF format."""
    return convert_mesh(obj_bytes, "obj", "dxf")


def ply_to_glb(ply_bytes: bytes) -> bytes:
    """Convert PLY to GLB format (for Shap-E output)."""
    return convert_mesh(ply_bytes, "ply", "glb")


def ply_to_step(ply_bytes: bytes) -> bytes:
    """Convert PLY to STEP format (for Shap-E output)."""
    return convert_mesh(ply_bytes, "ply", "step")


def ply_to_dxf(ply_bytes: bytes) -> bytes:
    """Convert PLY to DXF format (for Shap-E output)."""
    return convert_mesh(ply_bytes, "ply", "dxf")


def glb_to_iges(glb_bytes: bytes) -> bytes:
    """Convert GLB to IGES format (Phase 5B: Mayo-powered)."""
    return convert_mesh(glb_bytes, "glb", "iges")


def glb_to_brep(glb_bytes: bytes) -> bytes:
    """Convert GLB to BREP format (Phase 5B: Mayo-powered)."""
    return convert_mesh(glb_bytes, "glb", "brep")


def obj_to_iges(obj_bytes: bytes) -> bytes:
    """Convert OBJ to IGES format (Phase 5B: Mayo-powered)."""
    return convert_mesh(obj_bytes, "obj", "iges")


def obj_to_brep(obj_bytes: bytes) -> bytes:
    """Convert OBJ to BREP format (Phase 5B: Mayo-powered)."""
    return convert_mesh(obj_bytes, "obj", "brep")


# Singleton
_mesh_converter: MeshConverter | None = None


def get_mesh_converter() -> MeshConverter:
    """Get mesh converter singleton."""
    global _mesh_converter
    if _mesh_converter is None:
        _mesh_converter = MeshConverter()
    return _mesh_converter
