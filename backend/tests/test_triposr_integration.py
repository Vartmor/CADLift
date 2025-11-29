#!/usr/bin/env python3
"""
Basic integration tests for TripoSR (Phase 2 image-to-3D).

These tests avoid heavy generation; they validate structure and graceful
handling when dependencies are missing.
"""
import asyncio
from pathlib import Path
from io import BytesIO

import pytest


def test_triposr_service_structure():
    from app.services.triposr import get_triposr_service

    service = get_triposr_service()
    assert hasattr(service, "generate_from_image")
    assert hasattr(service, "_load_model")
    assert hasattr(service, "_load_image")

    # If disabled (missing deps), ensure flag is false
    if not service.enabled:
        pytest.skip("TripoSR dependencies not installed; skipping heavy tests")

    # Smoke test image loader (in-memory blank)
    from PIL import Image
    import numpy as np

    arr = (np.ones((16, 16, 3)) * 255).astype("uint8")
    img = Image.fromarray(arr, mode="RGB")
    buf = BytesIO()
    img.save(buf, format="PNG")
    loaded = service._load_image(buf.getvalue())
    assert loaded.size == (16, 16)


@pytest.mark.asyncio
async def test_ai_pipeline_image_metadata():
    """Ensure AI pipeline returns metadata for image source even if generation fails/disabled."""
    from app.pipelines.ai import run_ai_pipeline
    from app.services.triposr import get_triposr_service

    service = get_triposr_service()
    if service.enabled:
        pytest.skip("TripoSR enabled; skipping heavy generation in CI")

    result = await run_ai_pipeline(
        prompt="tests/test_data/sample.png",  # path placeholder
        params={"detail": 50},
        source_type="image",
    )
    assert "metadata" in result
    assert result["metadata"]["pipeline"] == "ai"
    assert result["metadata"]["source_type"] == "image"
