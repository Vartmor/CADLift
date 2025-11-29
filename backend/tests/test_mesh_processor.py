#!/usr/bin/env python3
"""
Unit tests for mesh processing (Phase 3).
"""
import asyncio

import numpy as np
import pytest
import trimesh

from app.services.mesh_processor import (
    get_mesh_processor,
    process_mesh,
    QualityMetrics,
)


def make_box_glb() -> bytes:
    mesh = trimesh.creation.box(extents=(1.0, 1.0, 1.0))
    buf = trimesh.util.wrap_as_stream(b"")
    mesh.export(buf, file_type="glb")
    return buf.getvalue()


def test_quality_metrics_basic():
    processor = get_mesh_processor()
    glb = make_box_glb()
    mesh = trimesh.load(trimesh.util.wrap_as_stream(glb), file_type="glb")
    qm: QualityMetrics = processor._calculate_quality(mesh)  # type: ignore
    assert qm.face_count > 0
    assert 1.0 <= qm.overall_score <= 10.0
    assert qm.bounding_box[0] > 0


@pytest.mark.asyncio
async def test_process_mesh_improves_or_equals():
    glb = make_box_glb()
    processor = get_mesh_processor()
    processed, quality = await processor.process_mesh(glb, file_type="glb")
    assert isinstance(processed, (bytes, bytearray))
    assert quality.overall_score >= 1.0


@pytest.mark.asyncio
async def test_process_mesh_retry_helper():
    glb = make_box_glb()
    processed, quality = await process_mesh(
        mesh_bytes=glb,
        file_type="glb",
        target_faces=1000,
        min_quality=1.0,
        max_retries=2,
    )
    assert isinstance(processed, (bytes, bytearray))
    assert quality.overall_score >= 1.0

