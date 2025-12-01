import asyncio
from pathlib import Path

import cv2
import numpy as np
import pytest

from app.db.session import AsyncSessionLocal
from app.models import File as FileModel, Job
from app.pipelines import image as image_pipeline
from app.services.storage import storage_service


def _sample_image_bytes() -> bytes:
    image = np.full((64, 64, 3), 255, dtype=np.uint8)
    cv2.circle(image, (32, 32), 18, (0, 0, 0), thickness=2)
    success, buffer = cv2.imencode(".png", image)
    assert success
    return buffer.tobytes()


@pytest.mark.asyncio
async def test_image_pipeline_prefers_triposr(monkeypatch, tmp_path: Path):
    """Ensure image pipeline short-circuits to TripoSR when available."""

    async def fake_run_ai(prompt: str, params: dict, source_type: str = "image") -> dict:
        return {
            "metadata": {
                "pipeline": "ai",
                "provider": "triposr_test",
                "quality_metrics": {"processing_quality_score": 9.1},
            },
            "outputs": {
                "glb": b"glb-bytes",
                "obj": b"obj-bytes",
                "dxf": b"dxf-bytes",
                "step": b"step-bytes",
            },
            "error": None,
            "fallback_used": False,
        }

    monkeypatch.setattr(image_pipeline, "run_ai_pipeline", fake_run_ai)

    async with AsyncSessionLocal() as session:
        job = Job(job_type="image", mode="image_to_3d", status="queued", params={"use_triposr": True})
        session.add(job)
        await session.flush()

        img_bytes = _sample_image_bytes()
        storage_key, size = storage_service.save_bytes(
            img_bytes,
            role="input",
            job_id=job.id,
            filename="triposr_input.png",
        )
        file_rec = FileModel(
            user_id=job.user_id,
            job_id=job.id,
            role="input",
            storage_key=storage_key,
            original_name="triposr_input.png",
            mime_type="image/png",
            size_bytes=size,
        )
        session.add(file_rec)
        await session.flush()
        job.input_file_id = file_rec.id
        await session.commit()

        await image_pipeline.run(job, session)
        await session.commit()
        await session.refresh(job)

        assert job.status == "completed"
        assert job.output_file_id is not None
        params = job.params or {}
        assert params.get("ai_metadata", {}).get("provider") == "triposr_test"
        assert params.get("glb_file_id") is not None
        assert params.get("step_file_id") is not None
