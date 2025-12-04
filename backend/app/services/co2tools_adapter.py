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
from typing import Optional


class Co2ToolsError(RuntimeError):
    """Wrapper error for co2tools-related failures."""


class Co2ToolsService:
    def __init__(self) -> None:
        self._logger = logging.getLogger("cadlift.service.co2tools")
        self._builder_cls = self._import_builder()
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

                return Builder
            except Exception as exc:  # noqa: BLE001
                # Try the next candidate
                self._logger.debug("co2tools import failed", extra={"candidate": str(candidate), "error": str(exc)})
                continue

        self._logger.warning("co2tools unavailable; STL generation via co2tools will be skipped")
        return None

    def dxf_bytes_to_stl(
        self,
        dxf_bytes: bytes,
        *,
        extrude_height: float,
        layer_cut: str = "CUT",
        layer_holes: Optional[str] = None,
        layer_holes2: Optional[str] = None,
    ) -> bytes:
        """
        Build an STL mesh from DXF content using co2tools logic.

        Args:
            dxf_bytes: DXF file content.
            extrude_height: Height to extrude (mm).
            layer_cut: DXF layer name that contains the cut/footprint polylines.
            layer_holes: Optional holes layer name.
            layer_holes2: Optional secondary holes layer name.
        """
        if not self.enabled or self._builder_cls is None:
            raise Co2ToolsError("co2tools is not available")

        try:
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

        except Co2ToolsError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise Co2ToolsError(f"co2tools STL generation failed: {exc}") from exc


_service: Co2ToolsService | None = None


def get_co2tools_service() -> Co2ToolsService:
    global _service
    if _service is None:
        _service = Co2ToolsService()
    return _service
