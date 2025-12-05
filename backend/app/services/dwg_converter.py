"""
DWG to DXF converter service using ODA File Converter.

ODA File Converter is a free tool from Open Design Alliance that converts
between DWG and DXF formats. This service wraps the command-line tool.
"""

from __future__ import annotations

import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger("cadlift.service.dwg_converter")


class DwgConverterError(RuntimeError):
    """Error during DWG conversion."""


class DwgConverterService:
    """Service for converting DWG files to DXF using ODA File Converter."""

    # Common installation paths for ODA File Converter
    DEFAULT_PATHS = [
        r"C:\Program Files\ODA\ODAFileConverter 26.10.0\ODAFileConverter.exe",
        r"C:\Program Files\ODA\ODAFileConverter 25.12.0\ODAFileConverter.exe",
        r"C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe",
        r"C:\Program Files (x86)\ODA\ODAFileConverter\ODAFileConverter.exe",
        "/usr/bin/ODAFileConverter",
        "/usr/local/bin/ODAFileConverter",
    ]

    def __init__(self, converter_path: Optional[str] = None) -> None:
        self._converter_path = converter_path or self._find_converter()
        self.enabled = self._converter_path is not None and Path(self._converter_path).exists()
        
        if self.enabled:
            logger.info(f"DWG converter initialized at: {self._converter_path}")
        else:
            logger.warning("ODA File Converter not found; DWG conversion disabled")

    def _find_converter(self) -> Optional[str]:
        """Find ODA File Converter in common installation paths."""
        # Check environment variable first
        env_path = os.environ.get("ODA_FILE_CONVERTER")
        if env_path and Path(env_path).exists():
            return env_path

        # Check common paths
        for path in self.DEFAULT_PATHS:
            if Path(path).exists():
                return path

        return None

    def convert_dwg_to_dxf(
        self,
        dwg_bytes: bytes,
        *,
        output_version: str = "ACAD2018",
        output_format: str = "DXF",
    ) -> bytes:
        """
        Convert DWG file bytes to DXF format.

        Args:
            dwg_bytes: DWG file content.
            output_version: Output DXF version (ACAD2018, ACAD2013, ACAD2010, etc.)
            output_format: Output format, typically "DXF" for ASCII DXF.

        Returns:
            DXF file bytes.
        """
        if not self.enabled:
            raise DwgConverterError("ODA File Converter is not available")

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)
                input_dir = tmp_path / "input"
                output_dir = tmp_path / "output"
                input_dir.mkdir()
                output_dir.mkdir()

                # Write DWG file
                dwg_path = input_dir / "input.dwg"
                dwg_path.write_bytes(dwg_bytes)

                # Run ODA File Converter
                # Syntax: ODAFileConverter <input_folder> <output_folder> <output_version> <output_type> <recursive> <audit>
                # output_type: 0 = DWG binary, 1 = DXF binary, 2 = DXF ASCII
                cmd = [
                    self._converter_path,
                    str(input_dir),
                    str(output_dir),
                    output_version,
                    "DXF",  # Output file type
                    "0",    # Recursive: 0 = no
                    "1",    # Audit: 1 = yes (repairs errors)
                ]

                logger.info(f"Running ODA converter: {' '.join(cmd)}")

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120,  # 2 minute timeout
                )

                if result.returncode != 0:
                    logger.error(f"ODA converter error: {result.stderr}")
                    raise DwgConverterError(f"Conversion failed: {result.stderr}")

                # Find output DXF file
                dxf_files = list(output_dir.glob("*.dxf"))
                if not dxf_files:
                    raise DwgConverterError("No DXF output produced by converter")

                dxf_path = dxf_files[0]
                logger.info(f"Conversion successful: {dxf_path.name}")

                return dxf_path.read_bytes()

        except subprocess.TimeoutExpired:
            raise DwgConverterError("Conversion timed out after 2 minutes")
        except DwgConverterError:
            raise
        except Exception as exc:
            raise DwgConverterError(f"DWG conversion failed: {exc}") from exc


_service: DwgConverterService | None = None


def get_dwg_converter_service() -> DwgConverterService:
    """Get singleton instance of DWG converter service."""
    global _service
    if _service is None:
        _service = DwgConverterService()
    return _service
