import io
import json
from pathlib import Path

import ezdxf
import cv2
import numpy as np

from fastapi.testclient import TestClient

from app.main import app


def _sample_dxf_bytes() -> bytes:
    doc = ezdxf.new()
    msp = doc.modelspace()
    msp.add_lwpolyline([(0, 0), (10, 0), (10, 10), (0, 10)], close=True)
    buffer = io.StringIO()
    doc.write(buffer)
    return buffer.getvalue().encode("utf-8")


def test_create_job_without_file(tmp_path, monkeypatch):
    client = TestClient(app)
    response = client.post(
        "/api/v1/jobs",
        data={
            "job_type": "cad",
            "mode": "2d_to_3d",
        },
    )
    assert response.status_code == 201
    job = response.json()
    assert job["status"] == "failed"
    assert job["job_type"] == "cad"
    assert job["output_file_id"] is None


def test_create_job_with_file(tmp_path):
    client = TestClient(app)
    files = {"upload": ("plan.dxf", _sample_dxf_bytes(), "application/dxf")}
    response = client.post(
        "/api/v1/jobs",
        data={
            "job_type": "cad",
            "mode": "2d_to_3d",
        },
        files=files,
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["input_file_id"] is not None
    assert payload["output_file_id"] is not None
    job_id = payload["id"]
    response = client.get(f"/api/v1/jobs/{job_id}")
    assert response.status_code == 200
    job = response.json()
    assert job["status"] == "completed"
    output_dir = Path("storage") / job_id / "output"
    dxf_files = list(output_dir.glob("*.dxf"))
    assert dxf_files, "DXF output not found"
    assert dxf_files[0].stat().st_size > 0
    step_dir = Path("storage") / job_id / "output_step"
    step_files = list(step_dir.glob("*.step"))
    assert step_files, "STEP output not found"
    assert step_files[0].stat().st_size > 0

    download = client.get(f"/api/v1/files/{job['output_file_id']}")
    assert download.status_code == 200
    assert b"SECTION" in download.content  # DXF header present


def _sample_image_bytes() -> bytes:
    image = np.full((128, 128, 3), 255, dtype=np.uint8)
    cv2.rectangle(image, (24, 24), (104, 104), (0, 0, 0), thickness=2)
    success, buffer = cv2.imencode(".png", image)
    assert success
    return buffer.tobytes()


def test_image_job_without_file():
    client = TestClient(app)
    response = client.post(
        "/api/v1/jobs",
        data={
            "job_type": "image",
            "mode": "image_to_3d",
        },
    )
    assert response.status_code == 201
    job = response.json()
    assert job["status"] == "failed"
    assert job["error_code"] == "SYS_FILE_NOT_FOUND"  # Updated to expect specific error code (Phase 3.1)
    assert job["output_file_id"] is None


def test_create_image_job_with_file(tmp_path):
    client = TestClient(app)
    files = {"upload": ("sketch.png", _sample_image_bytes(), "image/png")}
    response = client.post(
        "/api/v1/jobs",
        data={
            "job_type": "image",
            "mode": "image_to_3d",
        },
        files=files,
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["output_file_id"] is not None
    job_id = payload["id"]
    response = client.get(f"/api/v1/jobs/{job_id}")
    assert response.status_code == 200
    job = response.json()
    assert job["status"] == "completed"
    assert job["error_code"] is None
    output_dir = Path("storage") / job_id / "output"
    dxf_files = list(output_dir.glob("*.dxf"))
    assert dxf_files
    step_dir = Path("storage") / job_id / "output_step"
    step_files = list(step_dir.glob("*.step"))
    assert step_files
    download = client.get(f"/api/v1/files/{job['output_file_id']}")
    assert download.status_code == 200
    assert b"SECTION" in download.content


def test_create_image_job_with_vision(monkeypatch):
    client = TestClient(app)
    from app.services import vision

    async def fake_vectorize(path):
        return [
            [[0.0, 0.0], [100.0, 0.0], [100.0, 100.0], [0.0, 100.0]],
        ]

    monkeypatch.setattr(vision.vision_service, "api_url", "http://fake")
    monkeypatch.setattr(vision.vision_service, "api_key", "test-key")
    monkeypatch.setattr(vision.vision_service, "vectorize", fake_vectorize)

    files = {"upload": ("sketch.png", _sample_image_bytes(), "image/png")}
    response = client.post(
        "/api/v1/jobs",
        data={
            "job_type": "image",
            "mode": "image_to_3d",
        },
        files=files,
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "completed"
    job_id = payload["id"]
    resp = client.get(f"/api/v1/jobs/{job_id}")
    assert resp.status_code == 200
    job = resp.json()
    assert job["status"] == "completed"


def test_prompt_job_without_prompt():
    client = TestClient(app)
    response = client.post(
        "/api/v1/jobs",
        data={
            "job_type": "prompt",
            "mode": "prompt_to_3d",
        },
    )
    assert response.status_code == 201
    job = response.json()
    assert job["status"] == "failed"
    assert job["error_code"] == "PROMPT_EMPTY"  # Updated to expect specific error code (Phase 3.1)
    assert job["output_file_id"] is None


def test_prompt_job_with_prompt():
    client = TestClient(app)
    prompt_params = {"prompt": "Design a 6000x4000 hall height 3m"}
    response = client.post(
        "/api/v1/jobs",
        data={
            "job_type": "prompt",
            "mode": "prompt_to_3d",
            "params": json.dumps(prompt_params),
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["output_file_id"] is not None
    job_id = payload["id"]

    response = client.get(f"/api/v1/jobs/{job_id}")
    assert response.status_code == 200
    job = response.json()
    assert job["status"] == "completed"
    assert job["error_code"] is None
    assert job["params"]["instructions"]["rooms"][0]["width"] == 6000.0
    assert job["params"]["instructions"]["extrude_height"] == 3000.0
    output_dir = Path("storage") / job_id / "output"
    dxf_files = list(output_dir.glob("*.dxf"))
    assert dxf_files
    step_dir = Path("storage") / job_id / "output_step"
    step_files = list(step_dir.glob("*.step"))
    assert step_files
    assert job["params"].get("step_file_id") is not None
    download = client.get(f"/api/v1/files/{job['output_file_id']}")
    assert download.status_code == 200
    assert b"SECTION" in download.content


def test_prompt_job_with_llm(monkeypatch):
    from app.services import llm

    async def fake_generate(prompt_text: str):
        return {
            "rooms": [{"name": "llm_room", "width": 2000, "length": 3000}],
            "corridor_gap": 0,
            "extrude_height": 1500,
        }

    monkeypatch.setattr(llm.llm_service, "provider", "openai")
    monkeypatch.setattr(llm.llm_service, "api_key", "test-key")
    monkeypatch.setattr(llm.llm_service, "generate_instructions", fake_generate)

    client = TestClient(app)
    prompt_params = {"prompt": "LLM driven prompt"}
    response = client.post(
        "/api/v1/jobs",
        data={
            "job_type": "prompt",
            "mode": "prompt_to_3d",
            "params": json.dumps(prompt_params),
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "completed"
    job_id = payload["id"]
    resp = client.get(f"/api/v1/jobs/{job_id}")
    assert resp.status_code == 200
    job = resp.json()
    assert job["params"]["instructions"]["rooms"][0]["width"] == 2000.0
