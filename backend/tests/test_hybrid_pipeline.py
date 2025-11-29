#!/usr/bin/env python3
"""
Hybrid pipeline tests (Phase 4).
"""
import asyncio

import pytest
import trimesh

from app.pipelines.hybrid import run_hybrid_pipeline


def make_box_glb(center=(0, 0, 0)) -> bytes:
    mesh = trimesh.creation.box(extents=(1.0, 1.0, 1.0))
    mesh.apply_translation(center)
    buf = trimesh.util.wrap_as_stream(b"")
    mesh.export(buf, file_type="glb")
    return buf.getvalue()


@pytest.mark.asyncio
async def test_hybrid_combines_meshes():
    ai_mesh = make_box_glb(center=(0, 0, 0))
    param_mesh = make_box_glb(center=(1.5, 0, 0))  # shifted to ensure non-overlap

    result = await run_hybrid_pipeline(
        ai_mesh=ai_mesh,
        ai_format="glb",
        param_mesh=param_mesh,
        param_format="glb",
        params={"param_offset": (0, 0, 0)},
    )

    assert "mesh" in result and len(result["mesh"]) > 0
    assert "metadata" in result and result["metadata"]["pipeline"] == "hybrid"
    assert "quality" in result and result["quality"]["overall_score"] >= 1.0
    assert "formats" in result and len(result["formats"]["glb"]) > 0


@pytest.mark.asyncio
async def test_hybrid_ai_only():
    ai_mesh = make_box_glb(center=(0, 0, 0))

    result = await run_hybrid_pipeline(ai_mesh=ai_mesh, ai_format="glb")

    assert "mesh" in result and len(result["mesh"]) > 0
    assert result["metadata"]["pipeline"] == "hybrid"
