"""
Error codes and error handling for CADLift.

Provides specific, actionable error codes and messages for all failure scenarios.
Phase 3.1: Production Hardening - Better Error Handling
"""

from __future__ import annotations
from dataclasses import dataclass


class ErrorCode:
    """
    Specific error codes for all failure scenarios.

    Format: {PIPELINE}_{CATEGORY}
    - CAD_xxx: DXF/CAD pipeline errors
    - IMG_xxx: Image pipeline errors
    - PROMPT_xxx: Prompt pipeline errors
    - GEO_xxx: Geometry generation errors
    - SYS_xxx: System-level errors
    """

    # DXF/CAD Pipeline Errors (CAD_xxx)
    CAD_NO_ENTITIES = "CAD_NO_ENTITIES"  # No entities found in DXF
    CAD_NO_CLOSED_SHAPES = "CAD_NO_CLOSED_SHAPES"  # No closed polylines/circles/arcs
    CAD_INVALID_FORMAT = "CAD_INVALID_FORMAT"  # Not a valid DXF file
    CAD_UNSUPPORTED_VERSION = "CAD_UNSUPPORTED_VERSION"  # DXF version not supported
    CAD_NO_VALID_LAYERS = "CAD_NO_VALID_LAYERS"  # Layer filter returned nothing
    CAD_READ_ERROR = "CAD_READ_ERROR"  # Failed to read DXF file
    CAD_TEXT_PARSE_ERROR = "CAD_TEXT_PARSE_ERROR"  # Failed to parse TEXT entities

    # Image Pipeline Errors (IMG_xxx)
    IMG_NO_CONTOURS = "IMG_NO_CONTOURS"  # No shapes detected in image
    IMG_INVALID_FORMAT = "IMG_INVALID_FORMAT"  # Not a valid image format
    IMG_READ_ERROR = "IMG_READ_ERROR"  # Failed to read image file
    IMG_TOO_SMALL = "IMG_TOO_SMALL"  # Image resolution too low
    IMG_TOO_LARGE = "IMG_TOO_LARGE"  # Image file or resolution too large
    IMG_EDGE_DETECTION_FAILED = "IMG_EDGE_DETECTION_FAILED"  # Canny edge detection failed

    # Prompt Pipeline Errors (PROMPT_xxx)
    PROMPT_EMPTY = "PROMPT_EMPTY"  # No prompt text provided
    PROMPT_LLM_FAILED = "PROMPT_LLM_FAILED"  # LLM failed after all retries
    PROMPT_INVALID_DIMENSIONS = "PROMPT_INVALID_DIMENSIONS"  # Room dimensions unrealistic
    PROMPT_VALIDATION_FAILED = "PROMPT_VALIDATION_FAILED"  # LLM response validation failed
    PROMPT_NO_ROOMS = "PROMPT_NO_ROOMS"  # No rooms in LLM response
    PROMPT_INVALID_JSON = "PROMPT_INVALID_JSON"  # LLM returned invalid JSON

    # Geometry Generation Errors (GEO_xxx)
    GEO_STEP_GENERATION_FAILED = "GEO_STEP_GENERATION_FAILED"  # STEP export failed
    GEO_DXF_GENERATION_FAILED = "GEO_DXF_GENERATION_FAILED"  # DXF export failed
    GEO_INVALID_POLYGON = "GEO_INVALID_POLYGON"  # Degenerate or invalid polygon
    GEO_BOOLEAN_OP_FAILED = "GEO_BOOLEAN_OP_FAILED"  # Boolean operation (offset/cut) failed
    GEO_NO_POLYGONS = "GEO_NO_POLYGONS"  # No valid polygons to process
    GEO_INVALID_HEIGHT = "GEO_INVALID_HEIGHT"  # Invalid extrusion height
    GEO_INVALID_WALL_THICKNESS = "GEO_INVALID_WALL_THICKNESS"  # Invalid wall thickness

    # System Errors (SYS_xxx)
    SYS_FILE_NOT_FOUND = "SYS_FILE_NOT_FOUND"  # Input file not found
    SYS_STORAGE_ERROR = "SYS_STORAGE_ERROR"  # Failed to save output file
    SYS_UNEXPECTED_ERROR = "SYS_UNEXPECTED_ERROR"  # Unexpected system error


@dataclass
class ErrorInfo:
    """
    User-friendly error information.

    Attributes:
        message: Clear description of what went wrong
        suggestion: Technical suggestion for fixing the issue
        user_action: What the user should do
        docs_url: Link to relevant documentation (optional)
    """
    message: str
    suggestion: str
    user_action: str
    docs_url: str | None = None


# Error message catalog - user-friendly explanations for each error code
ERROR_MESSAGES: dict[str, ErrorInfo] = {
    # CAD Pipeline Errors
    ErrorCode.CAD_NO_ENTITIES: ErrorInfo(
        message="DXF file contains no entities",
        suggestion="The DXF file appears to be empty. Ensure it was exported correctly from your CAD software.",
        user_action="Open the DXF in CAD software and verify it contains visible shapes. Re-export if necessary.",
    ),

    ErrorCode.CAD_NO_CLOSED_SHAPES: ErrorInfo(
        message="No closed shapes found in DXF file",
        suggestion="CADLift requires closed polylines, circles, or arcs. Open polylines are not supported.",
        user_action="In your CAD software, ensure all room outlines are closed shapes. Use PEDIT to close polylines.",
    ),

    ErrorCode.CAD_INVALID_FORMAT: ErrorInfo(
        message="File is not a valid DXF format",
        suggestion="The file may be corrupted or in an unsupported format.",
        user_action="Ensure the file has a .dxf extension and was exported as DXF (not DWG). Try re-exporting from CAD software.",
    ),

    ErrorCode.CAD_NO_VALID_LAYERS: ErrorInfo(
        message="Layer filter returned no entities",
        suggestion="The specified layers do not exist or contain no shapes.",
        user_action="Check your layer names in the DXF. Remove the layer filter or use valid layer names.",
    ),

    ErrorCode.CAD_READ_ERROR: ErrorInfo(
        message="Failed to read DXF file",
        suggestion="The DXF file may be corrupted or in an unsupported version.",
        user_action="Try opening the DXF in CAD software. If it works, re-export as DXF R2010 or later.",
    ),

    # Image Pipeline Errors
    ErrorCode.IMG_NO_CONTOURS: ErrorInfo(
        message="No shapes detected in image",
        suggestion="The image may have low contrast or no clear edges. Try preprocessing the image or adjusting detection parameters.",
        user_action="Increase contrast in your image editor, draw thicker lines, or adjust Canny threshold parameters.",
    ),

    ErrorCode.IMG_INVALID_FORMAT: ErrorInfo(
        message="Invalid image format",
        suggestion="Supported formats: PNG, JPG, JPEG, BMP. The file may be corrupted.",
        user_action="Convert your image to PNG or JPG format. Ensure the file is not corrupted.",
    ),

    ErrorCode.IMG_READ_ERROR: ErrorInfo(
        message="Failed to read image file",
        suggestion="The image file may be corrupted or in an unsupported format.",
        user_action="Try opening the image in an image viewer. If it doesn't work, the file is corrupted.",
    ),

    ErrorCode.IMG_TOO_SMALL: ErrorInfo(
        message="Image resolution too low",
        suggestion="Images must be at least 100×100 pixels for reliable detection.",
        user_action="Use a higher resolution scan or image (minimum 100×100 pixels).",
    ),

    ErrorCode.IMG_TOO_LARGE: ErrorInfo(
        message="Image file or resolution too large",
        suggestion="Maximum supported resolution: 10000×10000 pixels. Maximum file size: 20MB.",
        user_action="Resize or compress the image. Use PNG compression or reduce resolution.",
    ),

    # Prompt Pipeline Errors
    ErrorCode.PROMPT_EMPTY: ErrorInfo(
        message="No prompt text provided",
        suggestion="The 'prompt' field is required for text-to-3D generation.",
        user_action="Provide a description of the building or rooms you want to generate.",
    ),

    ErrorCode.PROMPT_LLM_FAILED: ErrorInfo(
        message="AI model failed to generate layout",
        suggestion="The LLM service is unavailable or returned invalid data after 3 attempts.",
        user_action="Try again in a few minutes. If the problem persists, simplify your prompt.",
    ),

    ErrorCode.PROMPT_INVALID_DIMENSIONS: ErrorInfo(
        message="Room dimensions are unrealistic",
        suggestion="Rooms must be between 1.5m × 1.5m (small closet) and 50m × 50m (large warehouse).",
        user_action="Check your prompt for typos. Use realistic room sizes (e.g., '4m × 3m bedroom').",
    ),

    ErrorCode.PROMPT_VALIDATION_FAILED: ErrorInfo(
        message="AI response validation failed",
        suggestion="The AI model returned invalid room data (missing dimensions, invalid format).",
        user_action="Try rephrasing your prompt to be more specific about room sizes and layout.",
    ),

    ErrorCode.PROMPT_NO_ROOMS: ErrorInfo(
        message="No rooms in AI response",
        suggestion="The AI model did not generate any rooms from your prompt.",
        user_action="Provide a clearer prompt with specific room names and dimensions (e.g., '10m × 8m office with 2 bedrooms').",
    ),

    # Geometry Errors
    ErrorCode.GEO_STEP_GENERATION_FAILED: ErrorInfo(
        message="3D STEP file generation failed",
        suggestion="The geometry may be too complex or contain degenerate shapes.",
        user_action="Simplify the geometry or reduce the number of rooms. Try using 2D-only mode.",
    ),

    ErrorCode.GEO_DXF_GENERATION_FAILED: ErrorInfo(
        message="DXF file generation failed",
        suggestion="Failed to create DXF output. This is usually a system error.",
        user_action="Try again. If the problem persists, contact support.",
    ),

    ErrorCode.GEO_INVALID_POLYGON: ErrorInfo(
        message="Invalid polygon detected",
        suggestion="One or more polygons have fewer than 3 points or are self-intersecting.",
        user_action="Ensure all shapes are simple, closed polygons with at least 3 vertices.",
    ),

    ErrorCode.GEO_BOOLEAN_OP_FAILED: ErrorInfo(
        message="Wall thickness operation failed",
        suggestion="Failed to offset the polygon to create wall thickness. The shape may be too small or complex.",
        user_action="Try with wall_thickness=0 (solid mode) or use simpler room shapes.",
    ),

    ErrorCode.GEO_NO_POLYGONS: ErrorInfo(
        message="No valid polygons to process",
        suggestion="All detected shapes were filtered out or invalid.",
        user_action="Check input file for valid closed shapes. Adjust filter parameters if using layer filtering.",
    ),

    ErrorCode.GEO_INVALID_HEIGHT: ErrorInfo(
        message="Invalid extrusion height",
        suggestion="Height must be between 100mm (0.1m) and 100m.",
        user_action="Use a realistic height value (typically 2.5m to 4m for rooms).",
    ),

    ErrorCode.GEO_INVALID_WALL_THICKNESS: ErrorInfo(
        message="Invalid wall thickness",
        suggestion="Wall thickness must be between 0mm (solid) and 5000mm (5m).",
        user_action="Use a realistic wall thickness (typically 200mm for residential, 0mm for solid mode).",
    ),

    # System Errors
    ErrorCode.SYS_FILE_NOT_FOUND: ErrorInfo(
        message="Input file not found",
        suggestion="The uploaded file could not be located in storage.",
        user_action="Re-upload the file. If the problem persists, contact support.",
    ),

    ErrorCode.SYS_STORAGE_ERROR: ErrorInfo(
        message="Failed to save output file",
        suggestion="Disk space may be full or there's a storage system issue.",
        user_action="Try again. If the problem persists, contact support.",
    ),

    ErrorCode.SYS_UNEXPECTED_ERROR: ErrorInfo(
        message="An unexpected error occurred",
        suggestion="This is an internal error that should be reported.",
        user_action="Try again. If the problem persists, contact support with the job ID.",
    ),
}


class CADLiftError(Exception):
    """
    Base exception for CADLift with error code and user-friendly message.

    Usage:
        raise CADLiftError(ErrorCode.CAD_NO_CLOSED_SHAPES, details="Found 0 polylines")
    """

    def __init__(self, error_code: str, details: str | None = None):
        self.error_code = error_code
        self.details = details

        # Get error info
        self.error_info = ERROR_MESSAGES.get(error_code)

        if self.error_info:
            message = self.error_info.message
            if details:
                message = f"{message} ({details})"
        else:
            message = f"Error: {error_code}"
            if details:
                message = f"{message} - {details}"

        super().__init__(message)

    def to_dict(self) -> dict:
        """Convert to dictionary for API response"""
        result = {
            "error_code": self.error_code,
            "message": str(self),
        }

        if self.error_info:
            result["suggestion"] = self.error_info.suggestion
            result["user_action"] = self.error_info.user_action
            if self.error_info.docs_url:
                result["docs_url"] = self.error_info.docs_url

        if self.details:
            result["details"] = self.details

        return result


def get_error_info(error_code: str) -> ErrorInfo | None:
    """Get error info for a given error code"""
    return ERROR_MESSAGES.get(error_code)
