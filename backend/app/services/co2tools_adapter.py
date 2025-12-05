from __future__ import annotations

"""
Thin adapter around the upstream co2tools STL builder so we can reuse it for 2D DXF
extrusion without adding a hard runtime dependency.

We try to import co2tools from the repository copy under docs/useful_projects/co2tools-master
or from the environment if it is already installed. If the package is unavailable,
the service reports disabled and callers can skip gracefully.
"""

import logging
import sys
import tempfile
from pathlib import Path
from typing import Optional, List


class Co2ToolsError(RuntimeError):
    """Wrapper error for co2tools-related failures."""


class Co2ToolsService:
    # Common layer names to try when auto-detecting
    COMMON_LAYER_NAMES = ["0", "CUT", "Footprint", "WALLS", "OUTLINE", "BOUNDARY", "PERIMETER"]

    def __init__(self) -> None:
        self._logger = logging.getLogger("cadlift.service.co2tools")
        self._builder_cls = self._import_builder()
        self._trimesh = self._import_trimesh()
        self.enabled = self._builder_cls is not None

    def _import_builder(self):
        """
        Attempt to import the co2tools Builder class.

        Search order:
        1) Already installed `co2tools` package.
        2) Vendored copy under docs/useful_projects/co2tools-master.
        """
        candidates = [
            None,  # environment import
            Path(__file__).resolve().parents[2] / "docs" / "useful_projects" / "co2tools-master",
        ]

        for candidate in candidates:
            try:
                if candidate is not None and candidate.exists():
                    candidate_str = str(candidate)
                    if candidate_str not in sys.path:
                        sys.path.insert(0, candidate_str)
                from co2tools.stl.builder import Builder  # type: ignore

                self._logger.info(f"co2tools Builder loaded from: {candidate or 'environment'}")
                return Builder
            except Exception as exc:  # noqa: BLE001
                # Try the next candidate
                self._logger.debug("co2tools import failed", extra={"candidate": str(candidate), "error": str(exc)})
                continue

        self._logger.warning("co2tools unavailable; STL generation via co2tools will be skipped")
        return None

    def _import_trimesh(self):
        """Import trimesh for mesh operations."""
        try:
            import trimesh
            return trimesh
        except ImportError:
            self._logger.warning("trimesh not available; GLB conversion will be disabled")
            return None

    def get_dxf_layers(self, dxf_bytes: bytes) -> List[str]:
        """
        Extract layer names from a DXF file.
        
        Args:
            dxf_bytes: DXF file content.
            
        Returns:
            List of layer names found in the DXF.
        """
        if self._trimesh is None:
            return []
            
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)
                dxf_path = tmp_path / "input.dxf"
                dxf_path.write_bytes(dxf_bytes)
                
                dxf = self._trimesh.load(str(dxf_path), file_type='dxf')
                layers = list(dxf.layers) if hasattr(dxf, 'layers') else []
                self._logger.info(f"DXF layers found: {layers}")
                return layers
        except Exception as exc:
            self._logger.warning(f"Failed to extract DXF layers: {exc}")
            return []

    def dxf_bytes_to_stl(
        self,
        dxf_bytes: bytes,
        *,
        extrude_height: float,
        layer_cut: Optional[str] = None,
        layer_holes: Optional[str] = None,
        layer_holes2: Optional[str] = None,
        auto_detect_layer: bool = True,
    ) -> bytes:
        """
        Build an STL mesh from DXF content using co2tools logic.

        Args:
            dxf_bytes: DXF file content.
            extrude_height: Height to extrude (mm).
            layer_cut: DXF layer name that contains the cut/footprint polylines.
                       If None and auto_detect_layer is True, will try common layer names.
            layer_holes: Optional holes layer name.
            layer_holes2: Optional secondary holes layer name.
            auto_detect_layer: If True, try common layer names if specified layer fails.
        """
        if not self.enabled or self._builder_cls is None:
            raise Co2ToolsError("co2tools is not available")

        # Determine which layers to try
        layers_to_try = []
        if layer_cut:
            layers_to_try.append(layer_cut)
        
        if auto_detect_layer:
            # Get actual layers from DXF
            dxf_layers = self.get_dxf_layers(dxf_bytes)
            # Add common layer names that exist in the DXF
            for common_layer in self.COMMON_LAYER_NAMES:
                if common_layer in dxf_layers and common_layer not in layers_to_try:
                    layers_to_try.append(common_layer)
            # Add all other layers as fallback
            for layer in dxf_layers:
                if layer not in layers_to_try:
                    layers_to_try.append(layer)
        
        if not layers_to_try:
            layers_to_try = ["0"]  # Ultimate fallback

        last_error = None
        for try_layer in layers_to_try:
            try:
                self._logger.info(f"Attempting STL generation with layer: {try_layer}")
                return self._build_stl(
                    dxf_bytes,
                    extrude_height=extrude_height,
                    layer_cut=try_layer,
                    layer_holes=layer_holes,
                    layer_holes2=layer_holes2,
                )
            except Exception as exc:
                self._logger.warning(f"Layer '{try_layer}' failed: {exc}")
                last_error = exc
                continue

        raise Co2ToolsError(f"co2tools STL generation failed with all layers. Last error: {last_error}")

    def _build_stl(
        self,
        dxf_bytes: bytes,
        *,
        extrude_height: float,
        layer_cut: str,
        layer_holes: Optional[str] = None,
        layer_holes2: Optional[str] = None,
    ) -> bytes:
        """Internal method to build STL with a specific layer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            dxf_path = tmp_path / "input.dxf"
            stl_name = "output.stl"
            dxf_path.write_bytes(dxf_bytes)

            options = {"LAYER_CUT": layer_cut}
            if layer_holes:
                options["LAYER_HOLES"] = layer_holes
            if layer_holes2:
                options["LAYER_HOLES2"] = layer_holes2

            builder = self._builder_cls(
                dxf_path.name,
                source_folder=str(tmp_path),
                target_folder=str(tmp_path),
                options=options,
            )
            builder.build([{"extrude": extrude_height}], stl_name)

            stl_path = tmp_path / stl_name
            if not stl_path.exists():
                raise Co2ToolsError("co2tools did not produce an STL file")

            return stl_path.read_bytes()

    def dxf_bytes_to_glb(
        self,
        dxf_bytes: bytes,
        *,
        extrude_height: float,
        layer_cut: Optional[str] = None,
        layer_holes: Optional[str] = None,
        layer_holes2: Optional[str] = None,
    ) -> bytes:
        """
        Build a GLB mesh from DXF content.
        
        First generates STL via co2tools, then converts to GLB using trimesh.

        Args:
            dxf_bytes: DXF file content.
            extrude_height: Height to extrude (mm).
            layer_cut: DXF layer name (auto-detected if None).
            layer_holes: Optional holes layer name.
            layer_holes2: Optional secondary holes layer name.
            
        Returns:
            GLB file bytes.
        """
        if self._trimesh is None:
            raise Co2ToolsError("trimesh not available for GLB conversion")

        # First get STL
        stl_bytes = self.dxf_bytes_to_stl(
            dxf_bytes,
            extrude_height=extrude_height,
            layer_cut=layer_cut,
            layer_holes=layer_holes,
            layer_holes2=layer_holes2,
        )

        # Convert STL to GLB
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)
                stl_path = tmp_path / "model.stl"
                glb_path = tmp_path / "model.glb"
                
                stl_path.write_bytes(stl_bytes)
                
                # Load STL mesh
                mesh = self._trimesh.load(str(stl_path), file_type='stl')
                
                # Export as GLB
                mesh.export(str(glb_path), file_type='glb')
                
                if not glb_path.exists():
                    raise Co2ToolsError("Failed to generate GLB file")
                
                return glb_path.read_bytes()
                
        except Co2ToolsError:
            raise
        except Exception as exc:
            raise Co2ToolsError(f"GLB conversion failed: {exc}") from exc

    def stl_bytes_to_glb(self, stl_bytes: bytes) -> bytes:
        """
        Convert STL bytes to GLB format.
        
        Args:
            stl_bytes: STL file content.
            
        Returns:
            GLB file bytes.
        """
        if self._trimesh is None:
            raise Co2ToolsError("trimesh not available for GLB conversion")

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)
                stl_path = tmp_path / "model.stl"
                glb_path = tmp_path / "model.glb"
                
                stl_path.write_bytes(stl_bytes)
                mesh = self._trimesh.load(str(stl_path), file_type='stl')
                mesh.export(str(glb_path), file_type='glb')
                
                return glb_path.read_bytes()
                
        except Exception as exc:
            raise Co2ToolsError(f"STL to GLB conversion failed: {exc}") from exc


_service: Co2ToolsService | None = None


def get_co2tools_service() -> Co2ToolsService:
    global _service
    if _service is None:
        _service = Co2ToolsService()
    return _service
