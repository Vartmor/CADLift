"""
Input validation utilities for CADLift.

Phase 3.4: Production Hardening - Input Validation & Security
Provides upload-time validation for DXF and image files.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import BinaryIO

import cv2
import ezdxf
import numpy as np

from app.core.errors import CADLiftError, ErrorCode
from app.core.logging import get_logger

logger = get_logger(__name__)

# File size limits (in bytes)
MAX_FILE_SIZES = {
    "dxf": 50 * 1024 * 1024,  # 50 MB
    "image": 20 * 1024 * 1024,  # 20 MB
    "default": 50 * 1024 * 1024,  # 50 MB default
}

# Image size limits
MIN_IMAGE_WIDTH = 100
MIN_IMAGE_HEIGHT = 100
MAX_IMAGE_WIDTH = 10000
MAX_IMAGE_HEIGHT = 10000


def validate_file_size(file_size: int, file_type: str = "default") -> None:
    """
    Validate file size against limits.

    Args:
        file_size: File size in bytes
        file_type: Type of file ("dxf", "image", or "default")

    Raises:
        CADLiftError: If file size exceeds limit
    """
    max_size = MAX_FILE_SIZES.get(file_type, MAX_FILE_SIZES["default"])

    if file_size > max_size:
        max_mb = max_size / (1024 * 1024)
        actual_mb = file_size / (1024 * 1024)
        raise CADLiftError(
            ErrorCode.SYS_STORAGE_ERROR,
            details=f"File size {actual_mb:.1f}MB exceeds limit of {max_mb:.0f}MB for {file_type} files",
        )

    logger.debug("file_size_validated", file_size=file_size, file_type=file_type, max_size=max_size)


def validate_dxf_file(file_data: bytes | BinaryIO, filename: str = "upload.dxf") -> tuple[bool, str | None]:
    """
    Validate DXF file before queuing for processing.

    Checks:
    - File is readable by ezdxf
    - File contains at least one entity
    - File has modelspace

    Args:
        file_data: DXF file content (bytes or file-like object)
        filename: Original filename for error messages

    Returns:
        tuple: (is_valid, error_message)
               If valid, returns (True, None)
               If invalid, returns (False, "error description")
    """
    try:
        # Write to temporary file for ezdxf to read
        with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tmp_file:
            if isinstance(file_data, bytes):
                tmp_file.write(file_data)
            else:
                tmp_file.write(file_data.read())
                file_data.seek(0)  # Reset file pointer
            tmp_path = tmp_file.name

        try:
            # Try to open with ezdxf
            doc = ezdxf.readfile(tmp_path)

            # Check if document has modelspace
            try:
                msp = doc.modelspace()
            except Exception:
                return False, "DXF file has no modelspace"

            # Check if modelspace has any entities
            entities = list(msp.query("*"))
            if len(entities) == 0:
                return False, "DXF file is empty (no entities found)"

            # Check for supported entity types
            supported_types = {"LWPOLYLINE", "POLYLINE", "LINE", "CIRCLE", "ARC", "SPLINE", "TEXT", "MTEXT"}
            entity_types = {e.dxftype() for e in entities}
            has_supported = bool(entity_types & supported_types)

            if not has_supported:
                found_types = ", ".join(sorted(entity_types))
                return False, f"DXF file contains no supported entities. Found: {found_types}"

            logger.info(
                "dxf_validation_success",
                filename=filename,
                entity_count=len(entities),
                entity_types=sorted(entity_types),
            )
            return True, None

        except ezdxf.DXFError as e:
            return False, f"Invalid DXF file format: {str(e)}"
        except Exception as e:
            return False, f"Failed to validate DXF: {str(e)}"
        finally:
            # Clean up temp file
            try:
                Path(tmp_path).unlink()
            except Exception:
                pass

    except Exception as e:
        return False, f"Failed to read file: {str(e)}"


def validate_image_file(file_data: bytes | BinaryIO, filename: str = "upload.png") -> tuple[bool, str | None]:
    """
    Validate image file before queuing for processing.

    Checks:
    - File is readable by OpenCV
    - Image has valid dimensions
    - Image is not too small or too large

    Args:
        file_data: Image file content (bytes or file-like object)
        filename: Original filename for error messages

    Returns:
        tuple: (is_valid, error_message)
               If valid, returns (True, None)
               If invalid, returns (False, "error description")
    """
    try:
        # Convert to numpy array
        if isinstance(file_data, bytes):
            nparr = np.frombuffer(file_data, np.uint8)
        else:
            nparr = np.frombuffer(file_data.read(), np.uint8)
            file_data.seek(0)  # Reset file pointer

        # Try to decode image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return False, "Invalid image format (OpenCV cannot decode)"

        # Check dimensions
        height, width = img.shape[:2]

        if height < MIN_IMAGE_HEIGHT or width < MIN_IMAGE_WIDTH:
            return False, f"Image too small ({width}×{height}). Minimum: {MIN_IMAGE_WIDTH}×{MIN_IMAGE_HEIGHT}"

        if height > MAX_IMAGE_HEIGHT or width > MAX_IMAGE_WIDTH:
            return False, f"Image too large ({width}×{height}). Maximum: {MAX_IMAGE_WIDTH}×{MAX_IMAGE_HEIGHT}"

        # Check if image is mostly blank (all pixels similar)
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        std_dev = np.std(gray)
        if std_dev < 5:  # Very low variance indicates blank image
            return False, "Image appears to be blank or has very low contrast"

        logger.info(
            "image_validation_success",
            filename=filename,
            width=width,
            height=height,
            channels=img.shape[2] if len(img.shape) == 3 else 1,
        )
        return True, None

    except Exception as e:
        return False, f"Failed to validate image: {str(e)}"


def validate_job_parameters(job_type: str, params: dict) -> tuple[bool, str | None]:
    """
    Validate job parameters for common issues.

    Args:
        job_type: Type of job ("cad", "image", "prompt")
        params: Job parameters dictionary

    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        # Validate extrude_height
        if "extrude_height" in params:
            height = params["extrude_height"]
            if not isinstance(height, (int, float)):
                return False, "extrude_height must be a number"
            if height <= 0:
                return False, "extrude_height must be positive"
            if height < 100 or height > 100000:
                return False, f"extrude_height {height}mm out of valid range (100-100000mm)"

        # Validate wall_thickness
        if "wall_thickness" in params:
            thickness = params["wall_thickness"]
            if not isinstance(thickness, (int, float)):
                return False, "wall_thickness must be a number"
            if thickness < 0:
                return False, "wall_thickness cannot be negative"
            if thickness > 5000:
                return False, f"wall_thickness {thickness}mm exceeds maximum (5000mm)"

        # Validate layers string
        if "layers" in params and params["layers"] is not None:
            layers = params["layers"]
            if not isinstance(layers, str):
                return False, "layers must be a string"
            if len(layers) > 500:
                return False, "layers string too long (max 500 characters)"

        # Validate prompt
        if job_type == "prompt" and "prompt" in params:
            prompt = params["prompt"]
            if not isinstance(prompt, str):
                return False, "prompt must be a string"
            if len(prompt.strip()) == 0:
                return False, "prompt cannot be empty"
            if len(prompt) > 5000:
                return False, "prompt too long (max 5000 characters)"

        return True, None

    except Exception as e:
        return False, f"Parameter validation error: {str(e)}"
