"""
Mayo CAD Converter Service (Phase 5B).

Professional-grade CAD format conversion using Mayo CLI.
Mayo is built on OpenCascade and provides true B-rep geometry export.

Installation:
- Windows: winget install --id Fougue.Mayo
- Linux: Download from https://github.com/fougue/mayo/releases
- macOS: Download from https://github.com/fougue/mayo/releases

Usage:
    mayo_service = get_mayo_service()
    if mayo_service.is_available():
        step_bytes = mayo_service.convert(glb_bytes, "glb", "step")
"""
from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Literal

logger = logging.getLogger("cadlift.services.mayo")

# Supported Mayo formats
MayoFormat = Literal[
    "step", "iges", "brep",  # B-rep CAD formats
    "stl", "obj", "glb", "gltf", "ply", "vrml", "amf", "off"  # Mesh formats
]

# Mayo export-capable formats (not all formats support export)
MAYO_EXPORT_FORMATS = {
    "step", "iges", "brep",  # CAD
    "stl", "obj", "glb", "gltf", "ply", "vrml", "amf", "off"  # Mesh
}


class MayoConversionError(Exception):
    """Raised when Mayo conversion fails."""
    pass


class MayoService:
    """
    Professional CAD conversion service using Mayo CLI.

    Mayo provides:
    - True B-rep (boundary representation) geometry
    - Professional-grade STEP/IGES export
    - Assembly structure preservation
    - Better CAD software compatibility
    """

    def __init__(self, mayo_exe: str = "mayoconv"):
        """
        Initialize Mayo service.

        Args:
            mayo_exe: Path to mayoconv executable (default: searches PATH)
        """
        self.mayo_exe = mayo_exe
        self._exe_path: str | None = None
        self._available: bool | None = None
        self._version: str | None = None

    def is_available(self) -> bool:
        """
        Check if Mayo is available on the system.

        Returns:
            True if mayoconv is in PATH and executable
        """
        if self._available is not None:
            return self._available

        # Check for CLI: prefer mayoconv, then mayo-conv, then default install path
        candidates = [
            self.mayo_exe,
            "mayo-conv",
            str(Path("C:/Program Files/Fougue/Mayo/mayo-conv.exe")),
        ]
        mayo_path = None
        for cand in candidates:
            found = shutil.which(cand)
            if not found and Path(cand).exists():
                found = str(Path(cand))
            if found:
                mayo_path = found
                break

        if not mayo_path:
            logger.info("Mayo not found in PATH. Install from: https://github.com/fougue/mayo/releases")
            self._available = False
            return False

        # Try to get version to verify it works
        try:
            result = subprocess.run(
                [mayo_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                self._version = result.stdout.strip()
                self._exe_path = mayo_path
                self._available = True
                logger.info(f"Mayo available: {self._version}")
                return True
        except Exception as exc:
            logger.warning(f"Mayo check failed: {exc}")

        self._available = False
        return False

    def get_version(self) -> str | None:
        """
        Get Mayo version string.

        Returns:
            Version string if available, None otherwise
        """
        if not self.is_available():
            return None
        return self._version

    def convert(
        self,
        input_bytes: bytes,
        from_format: str,
        to_format: MayoFormat,
        timeout: int = 120,
    ) -> bytes:
        """
        Convert file from one format to another using Mayo.

        Args:
            input_bytes: Input file bytes
            from_format: Source format (e.g., "glb", "stl", "step")
            to_format: Target format (e.g., "step", "iges", "brep")
            timeout: Conversion timeout in seconds (default: 120)

        Returns:
            Converted file bytes

        Raises:
            MayoConversionError: If conversion fails
            RuntimeError: If Mayo is not available
        """
        if not self.is_available():
            raise RuntimeError(
                "Mayo is not available. Install from: https://github.com/fougue/mayo/releases"
            )

        mayo_exec = self._exe_path or self.mayo_exe

        if to_format not in MAYO_EXPORT_FORMATS:
            raise MayoConversionError(
                f"Mayo does not support export to {to_format}. "
                f"Supported formats: {', '.join(sorted(MAYO_EXPORT_FORMATS))}"
            )

        # Create temporary directory for conversion
        with tempfile.TemporaryDirectory(prefix="mayo_convert_") as tmpdir:
            tmppath = Path(tmpdir)

            # Write input file
            input_file = tmppath / f"input.{from_format}"
            input_file.write_bytes(input_bytes)

            # Define output file
            output_file = tmppath / f"output.{to_format}"

            # Build Mayo command
            cmd = [
                mayo_exec,
                str(input_file),
                "-e", str(output_file),
                "--no-progress",  # Disable progress bar for cleaner logs
            ]

            logger.info(
                f"Mayo conversion: {from_format} → {to_format}",
                extra={"input_size": len(input_bytes), "timeout": timeout}
            )

            # Run Mayo conversion
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=tmpdir,
                )

                if result.returncode != 0:
                    error_msg = result.stderr or result.stdout or "Unknown error"
                    logger.error(
                        f"Mayo conversion failed: {error_msg}",
                        extra={"return_code": result.returncode}
                    )
                    raise MayoConversionError(f"Mayo conversion failed: {error_msg}")

                # Read output file
                if not output_file.exists():
                    raise MayoConversionError(
                        f"Mayo did not create output file: {output_file}"
                    )

                output_bytes = output_file.read_bytes()
                logger.info(
                    f"Mayo conversion successful",
                    extra={
                        "output_size": len(output_bytes),
                        "format": to_format
                    }
                )

                return output_bytes

            except subprocess.TimeoutExpired:
                logger.error(f"Mayo conversion timeout after {timeout}s")
                raise MayoConversionError(
                    f"Mayo conversion timeout after {timeout} seconds"
                )
            except Exception as exc:
                logger.exception(f"Mayo conversion error: {exc}")
                raise MayoConversionError(f"Mayo conversion error: {exc}") from exc

    def batch_convert(
        self,
        input_bytes: bytes,
        from_format: str,
        to_formats: list[MayoFormat],
        timeout: int = 180,
    ) -> dict[str, bytes]:
        """
        Convert input file to multiple formats in a single Mayo invocation.

        This is more efficient than multiple convert() calls.

        Args:
            input_bytes: Input file bytes
            from_format: Source format
            to_formats: List of target formats
            timeout: Conversion timeout in seconds (default: 180)

        Returns:
            Dictionary mapping format to converted bytes

        Raises:
            MayoConversionError: If conversion fails
            RuntimeError: If Mayo is not available
        """
        if not self.is_available():
            raise RuntimeError(
                "Mayo is not available. Install from: https://github.com/fougue/mayo/releases"
            )

        # Validate all formats
        unsupported = [fmt for fmt in to_formats if fmt not in MAYO_EXPORT_FORMATS]
        if unsupported:
            raise MayoConversionError(
                f"Unsupported export formats: {', '.join(unsupported)}"
            )

        with tempfile.TemporaryDirectory(prefix="mayo_batch_") as tmpdir:
            tmppath = Path(tmpdir)

            # Write input file
            input_file = tmppath / f"input.{from_format}"
            input_file.write_bytes(input_bytes)

            # Define output files
            output_files = {
                fmt: tmppath / f"output.{fmt}"
                for fmt in to_formats
            }

            # Build Mayo command with multiple -e flags
            cmd = [self.mayo_exe, str(input_file), "--no-progress"]
            for output_file in output_files.values():
                cmd.extend(["-e", str(output_file)])

            logger.info(
                f"Mayo batch conversion: {from_format} → {len(to_formats)} formats",
                extra={"formats": to_formats}
            )

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=tmpdir,
                )

                if result.returncode != 0:
                    error_msg = result.stderr or result.stdout or "Unknown error"
                    raise MayoConversionError(f"Mayo batch conversion failed: {error_msg}")

                # Read all output files
                outputs = {}
                for fmt, output_file in output_files.items():
                    if not output_file.exists():
                        logger.warning(f"Mayo did not create {fmt} output")
                        continue
                    outputs[fmt] = output_file.read_bytes()

                logger.info(
                    f"Mayo batch conversion successful: {len(outputs)}/{len(to_formats)} formats"
                )

                return outputs

            except subprocess.TimeoutExpired:
                raise MayoConversionError(
                    f"Mayo batch conversion timeout after {timeout} seconds"
                )
            except Exception as exc:
                raise MayoConversionError(f"Mayo batch conversion error: {exc}") from exc


# Singleton instance
_mayo_service: MayoService | None = None


def get_mayo_service() -> MayoService:
    """
    Get the singleton Mayo service instance.

    Returns:
        MayoService instance
    """
    global _mayo_service
    if _mayo_service is None:
        _mayo_service = MayoService()
    return _mayo_service
