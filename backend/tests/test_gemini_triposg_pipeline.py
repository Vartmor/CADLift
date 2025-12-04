import asyncio
from pathlib import Path

import pytest

from app.db.session import AsyncSessionLocal
from app.models import File as FileModel, Job
from app.pipelines import prompt as prompt_pipeline
from app.pipelines import image as image_pipeline
from app.services.storage import storage_service


class _FakeQuality:
    overall_score = 9.5
    face_count = 1234
    vertex_count = 567
    is_watertight = True


class _FakeConverter:
    def convert(self, data: bytes, input_fmt: str, output_fmt: str) -> bytes:
        return f"{output_fmt}".encode()


class _FakeGemini:
    def is_available(self) -> bool:
        return True

    def generate_image(self, prompt: str, aspect_ratio=None, resolution=None, model=None) -> bytes:
        return b"fake-image"


class _FakeTripoSG:
    def is_available(self) -> bool:
        return True

    def generate_mesh(self, image_bytes: bytes, faces=None, timeout=600) -> bytes:
        return b"fake-glb"


@pytest.mark.asyncio
async def test_prompt_pipeline_gemini_triposg(monkeypatch, tmp_path: Path):
    pytest.skip("Gemini image generation removed; OpenAI path only")

    monkeypatch.setattr(prompt_pipeline, "get_gemini_image_service", lambda: _FakeGemini())
    monkeypatch.setattr(prompt_pipeline, "get_triposg_service", lambda: _FakeTripoSG())
    monkeypatch.setattr(prompt_pipeline, "get_mesh_converter", lambda: _FakeConverter())
    monkeypatch.setattr(prompt_pipeline, "process_mesh", lambda data, **kwargs: (data, _FakeQuality()))

    async with AsyncSessionLocal() as session:
        job = Job(
            job_type="prompt",
            mode="prompt_to_3d",
            status="queued",
            params={"prompt": "organic dragon statue", "use_gemini_triposg": True, "detail": 80},
        )
        session.add(job)
        await session.flush()

        await prompt_pipeline.run(job, session)
        await session.commit()
        await session.refresh(job)

        assert job.status == "completed"
        assert job.output_file_id is not None
        assert job.params.get("ai_metadata", {}).get("provider") == "gemini+triposg"


@pytest.mark.asyncio
async def test_image_pipeline_triposg(monkeypatch, tmp_path: Path):
    """Ensure image pipeline can short-circuit to TripoSG when requested."""

    monkeypatch.setattr(image_pipeline, "get_triposg_service", lambda: _FakeTripoSG())
    monkeypatch.setattr(image_pipeline, "get_mesh_converter", lambda: _FakeConverter())
    monkeypatch.setattr(image_pipeline, "process_mesh", lambda data, **kwargs: (data, _FakeQuality()))

    img_bytes = b"\x89PNG\r\n"  # fake data
    async with AsyncSessionLocal() as session:
        job = Job(
            job_type="image",
            mode="image_to_3d",
            status="queued",
            params={"use_triposg": True, "detail": 70},
        )
        session.add(job)
        await session.flush()

        storage_key, size = storage_service.save_bytes(
            img_bytes,
            role="input",
            job_id=job.id,
            filename="input.png",
        )
        file_rec = FileModel(
            user_id=None,
            job_id=job.id,
            role="input",
            storage_key=storage_key,
            original_name="input.png",
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
        assert job.params.get("ai_metadata", {}).get("provider") == "triposg_local"
