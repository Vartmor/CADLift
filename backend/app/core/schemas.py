"""
Pydantic schemas for request validation.

Phase 3.4: Production Hardening - Input Validation
Provides type-safe parameter validation for all job endpoints.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class CADJobParams(BaseModel):
    """Parameters for CAD pipeline jobs."""

    extrude_height: float = Field(
        default=3000,
        ge=100,
        le=100000,
        description="Wall height in millimeters (100mm - 100000mm)",
    )
    wall_thickness: float = Field(
        default=200,
        ge=0,
        le=5000,
        description="Wall thickness in millimeters (0mm - 5000mm, 0 = solid)",
    )
    layers: str | None = Field(
        default=None,
        max_length=500,
        description="Comma-separated list of DXF layer names to include",
    )
    only_2d: bool = Field(
        default=False,
        description="Generate only 2D footprints (skip 3D geometry)",
    )

    @field_validator("layers")
    @classmethod
    def validate_layers(cls, v: str | None) -> str | None:
        if v is not None and len(v.strip()) == 0:
            return None
        return v


class ImageJobParams(BaseModel):
    """Parameters for image pipeline jobs."""

    extrude_height: float = Field(
        default=3000,
        ge=100,
        le=100000,
        description="Wall height in millimeters (100mm - 100000mm)",
    )
    wall_thickness: float = Field(
        default=200,
        ge=0,
        le=5000,
        description="Wall thickness in millimeters (0mm - 5000mm, 0 = solid)",
    )
    use_vision: bool = Field(
        default=False,
        description="Use Claude Vision API for advanced image understanding",
    )
    canny_threshold1: int = Field(
        default=50,
        ge=0,
        le=255,
        description="Canny edge detection lower threshold",
    )
    canny_threshold2: int = Field(
        default=150,
        ge=0,
        le=255,
        description="Canny edge detection upper threshold",
    )
    douglas_peucker_epsilon: float = Field(
        default=2.0,
        ge=0.1,
        le=50.0,
        description="Douglas-Peucker simplification epsilon",
    )
    only_2d: bool = Field(
        default=False,
        description="Generate only 2D footprints (skip 3D geometry)",
    )


class PromptJobParams(BaseModel):
    """Parameters for prompt pipeline jobs."""

    prompt: str = Field(
        ...,  # Required
        min_length=1,
        max_length=5000,
        description="Natural language description of the building/space",
    )
    extrude_height: float = Field(
        default=3000,
        ge=100,
        le=100000,
        description="Wall height in millimeters (100mm - 100000mm)",
    )
    wall_thickness: float = Field(
        default=200,
        ge=0,
        le=5000,
        description="Wall thickness in millimeters (0mm - 5000mm, 0 = solid)",
    )
    use_llm: bool = Field(
        default=True,
        description="Use LLM to generate layout (false = manual instruction format)",
    )

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        if len(v.strip()) == 0:
            raise ValueError("Prompt cannot be empty or whitespace only")
        return v.strip()


class JobCreateRequest(BaseModel):
    """Request body for creating a job."""

    job_type: Literal["cad", "image", "prompt"] = Field(
        ...,
        description="Type of conversion job",
    )
    mode: str = Field(
        default="2d_to_3d",
        description="Processing mode",
    )
    params: dict = Field(
        default_factory=dict,
        description="Job-specific parameters",
    )

    def get_validated_params(self) -> CADJobParams | ImageJobParams | PromptJobParams:
        """
        Get validated parameters based on job type.

        Returns:
            Validated parameter model

        Raises:
            ValueError: If parameters are invalid
        """
        if self.job_type == "cad":
            return CADJobParams(**self.params)
        elif self.job_type == "image":
            return ImageJobParams(**self.params)
        elif self.job_type == "prompt":
            return PromptJobParams(**self.params)
        else:
            raise ValueError(f"Unsupported job type: {self.job_type}")


class FileSizeLimit(BaseModel):
    """File size limit configuration."""

    dxf: int = Field(default=50 * 1024 * 1024, description="Max DXF file size in bytes")
    image: int = Field(default=20 * 1024 * 1024, description="Max image file size in bytes")
    default: int = Field(default=50 * 1024 * 1024, description="Default max file size in bytes")
