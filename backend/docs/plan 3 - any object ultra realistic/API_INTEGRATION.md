# API Integration Guide - Shap-E & TripoSR

**Date**: 2025-11-27
**Version**: 1.0

---

## Overview

This guide covers integrating external AI services for 3D generation:
1. **OpenAI Shap-E** - Text-to-3D generation
2. **TripoSR** - Image-to-3D generation (local model)
3. **Supporting services** - Mesh processing, quality validation

---

## 1. OpenAI Shap-E Integration

### Setup

#### Prerequisites
```bash
# Install OpenAI SDK
pip install openai>=1.0.0

# Install mesh processing libraries
pip install trimesh>=4.0.0 pygltflib>=1.16.0 pillow>=10.0.0
```

#### API Key Configuration
```python
# .env
OPENAI_API_KEY=sk-proj-...
SHAP_E_MODEL=shap-e
SHAP_E_GUIDANCE_SCALE=15.0
SHAP_E_NUM_STEPS=64
SHAP_E_TIMEOUT=120
```

### Implementation

#### Service Class

**File**: `backend/app/services/shap_e.py`

```python
from __future__ import annotations

import asyncio
import logging
from typing import Optional
import httpx
from openai import AsyncOpenAI
import trimesh
from io import BytesIO

logger = logging.getLogger("cadlift.services.shap_e")

class ShapEService:
    """OpenAI Shap-E text-to-3D generation service."""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "shap-e"
        self.enabled = bool(api_key and api_key.startswith("sk-"))

    async def generate_from_text(
        self,
        prompt: str,
        guidance_scale: float = 15.0,
        num_steps: int = 64,
        frame_size: int = 256,
    ) -> bytes:
        """
        Generate 3D mesh from text prompt using Shap-E.

        Args:
            prompt: Text description of object
            guidance_scale: Classifier-free guidance scale (higher = more faithful)
            num_steps: Number of diffusion steps (higher = better quality)
            frame_size: Output resolution (64, 128, 256)

        Returns:
            GLB file bytes

        Raises:
            ShapEAPIError: If generation fails
        """
        if not self.enabled:
            raise ShapEAPIError("Shap-E service not enabled (missing API key)")

        # Optimize prompt for Shap-E
        optimized_prompt = self._optimize_prompt(prompt)

        logger.info(
            "Generating 3D from text with Shap-E",
            extra={
                "prompt": prompt,
                "optimized": optimized_prompt,
                "guidance_scale": guidance_scale,
                "num_steps": num_steps,
            }
        )

        try:
            # Call Shap-E API
            response = await self.client.images.generate(
                model=self.model,
                prompt=optimized_prompt,
                size=f"{frame_size}x{frame_size}",
                n=1,
                response_format="url"  # or "b64_json"
            )

            # NOTE: This is pseudocode - actual Shap-E API may differ
            # You'll need to check OpenAI's actual Shap-E endpoint
            mesh_url = response.data[0].url

            # Download mesh
            async with httpx.AsyncClient() as client:
                mesh_response = await client.get(mesh_url, timeout=120.0)
                mesh_response.raise_for_status()
                glb_bytes = mesh_response.content

            logger.info(
                "Shap-E generation successful",
                extra={"size_bytes": len(glb_bytes)}
            )

            return glb_bytes

        except Exception as e:
            logger.error(f"Shap-E generation failed: {e}")
            raise ShapEAPIError(f"Failed to generate 3D mesh: {e}")

    def _optimize_prompt(self, prompt: str) -> str:
        """
        Optimize prompt for better Shap-E results.

        Strategies:
        - Add "3D model of" prefix
        - Add quality keywords: "detailed", "high-quality"
        - Remove ambiguous terms
        - Simplify complex descriptions
        """
        # Remove filler words
        optimized = prompt.lower().strip()

        # Add 3D context if missing
        if "3d" not in optimized and "model" not in optimized:
            optimized = f"3D model of {optimized}"

        # Add quality keywords
        if "detailed" not in optimized and "quality" not in optimized:
            optimized = f"detailed {optimized}"

        # Shap-E works better with simple, clear prompts
        # Example: "Create a realistic dragon" → "detailed 3D model of a dragon"

        return optimized

    async def generate_batch(
        self,
        prompts: list[str],
        max_concurrent: int = 3
    ) -> list[bytes]:
        """
        Generate multiple meshes in batch with concurrency control.

        Args:
            prompts: List of text prompts
            max_concurrent: Max simultaneous API calls

        Returns:
            List of GLB bytes (same order as prompts)
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def generate_one(prompt: str) -> bytes:
            async with semaphore:
                return await self.generate_from_text(prompt)

        results = await asyncio.gather(
            *[generate_one(p) for p in prompts],
            return_exceptions=True
        )

        # Handle errors
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch generation failed for prompt {i}: {result}")
                results[i] = None

        return results


class ShapEAPIError(Exception):
    """Shap-E API error."""
    pass


# Singleton instance
_shap_e_service: Optional[ShapEService] = None

def get_shap_e_service() -> ShapEService:
    """Get Shap-E service singleton."""
    global _shap_e_service
    if _shap_e_service is None:
        import os
        api_key = os.getenv("OPENAI_API_KEY", "")
        _shap_e_service = ShapEService(api_key)
    return _shap_e_service
```

### Usage Example

```python
from app.services.shap_e import get_shap_e_service

# Generate mesh from text
service = get_shap_e_service()
glb_bytes = await service.generate_from_text(
    prompt="a detailed dragon statue",
    guidance_scale=15.0,
    num_steps=64
)

# Save to file
with open("dragon.glb", "wb") as f:
    f.write(glb_bytes)

# Load with trimesh
mesh = trimesh.load(BytesIO(glb_bytes), file_type="glb")
print(f"Vertices: {len(mesh.vertices)}, Faces: {len(mesh.faces)}")
```

### Cost Management

```python
class ShapECostTracker:
    """Track Shap-E API costs."""

    COST_PER_CALL = 0.10  # Estimate, check actual pricing

    def __init__(self):
        self.total_calls = 0
        self.total_cost = 0.0

    def record_call(self, prompt: str):
        """Record a Shap-E API call."""
        self.total_calls += 1
        self.total_cost += self.COST_PER_CALL

        logger.info(
            "Shap-E cost tracked",
            extra={
                "total_calls": self.total_calls,
                "total_cost": f"${self.total_cost:.2f}",
                "prompt": prompt[:50]
            }
        )

    def check_budget(self, monthly_budget: float = 500.0) -> bool:
        """Check if within budget."""
        return self.total_cost < monthly_budget
```

### Error Handling

```python
async def generate_with_retry(
    prompt: str,
    max_retries: int = 3
) -> bytes:
    """Generate with automatic retry on failure."""

    for attempt in range(max_retries):
        try:
            service = get_shap_e_service()
            return await service.generate_from_text(prompt)

        except ShapEAPIError as e:
            logger.warning(
                f"Shap-E attempt {attempt + 1} failed: {e}",
                extra={"prompt": prompt}
            )

            if attempt == max_retries - 1:
                raise

            # Exponential backoff
            await asyncio.sleep(2 ** attempt)

    raise ShapEAPIError("All retry attempts failed")
```

---

## 2. TripoSR Integration (Image-to-3D)

### Setup

#### Prerequisites
```bash
# Install PyTorch (GPU recommended)
pip install torch>=2.0.0 torchvision>=0.15.0

# Install TripoSR dependencies
pip install transformers>=4.35.0 trimesh>=4.0.0 rembg>=2.0.0

# Install additional utilities
pip install pillow>=10.0.0 numpy>=1.24.0
```

#### Model Download

```python
# Download TripoSR model (first run)
from transformers import AutoModel

model = AutoModel.from_pretrained(
    "stabilityai/TripoSR",
    trust_remote_code=True,
    cache_dir="/models/triposr"
)
```

### Implementation

**File**: `backend/app/services/triposr.py`

```python
from __future__ import annotations

import torch
import numpy as np
from PIL import Image
import trimesh
from io import BytesIO
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger("cadlift.services.triposr")

class TripoSRService:
    """Image-to-3D using TripoSR model."""

    def __init__(
        self,
        model_path: str = "/models/triposr",
        device: str = "cuda"
    ):
        self.device = device if torch.cuda.is_available() else "cpu"
        self.model_path = model_path
        self.model = None
        self._load_model()

        logger.info(
            "TripoSR service initialized",
            extra={"device": self.device, "model_path": model_path}
        )

    def _load_model(self):
        """Load TripoSR model."""
        from transformers import AutoModel

        try:
            self.model = AutoModel.from_pretrained(
                "stabilityai/TripoSR",
                trust_remote_code=True,
                cache_dir=self.model_path
            )
            self.model = self.model.to(self.device)
            self.model.eval()
            logger.info("TripoSR model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load TripoSR model: {e}")
            raise

    async def generate_from_image(
        self,
        image_path: str,
        mc_resolution: int = 256,
        remove_background: bool = True
    ) -> bytes:
        """
        Generate 3D mesh from single image.

        Args:
            image_path: Path to input image
            mc_resolution: Marching cubes resolution (64, 128, 256, 512)
            remove_background: Auto-remove background

        Returns:
            OBJ file bytes
        """
        logger.info(
            "Generating 3D from image with TripoSR",
            extra={"image": image_path, "resolution": mc_resolution}
        )

        # Load and preprocess image
        image = Image.open(image_path).convert("RGB")

        # Remove background if requested
        if remove_background:
            image = self._remove_background(image)

        # Resize to model input size (typically 256x256 or 512x512)
        image = image.resize((512, 512), Image.Resampling.LANCZOS)

        # Convert to tensor
        image_tensor = torch.from_numpy(np.array(image)).permute(2, 0, 1)
        image_tensor = image_tensor.float() / 255.0
        image_tensor = image_tensor.unsqueeze(0).to(self.device)

        # Generate 3D
        with torch.no_grad():
            # TripoSR generates mesh
            mesh = self.model.generate_mesh(
                image_tensor,
                mc_resolution=mc_resolution
            )

        # Convert to trimesh
        vertices = mesh.vertices.cpu().numpy()
        faces = mesh.faces.cpu().numpy()
        trimesh_obj = trimesh.Trimesh(vertices=vertices, faces=faces)

        # Export to OBJ
        obj_bytes = BytesIO()
        trimesh_obj.export(obj_bytes, file_type="obj")
        obj_bytes.seek(0)

        logger.info(
            "TripoSR generation successful",
            extra={
                "vertices": len(vertices),
                "faces": len(faces),
                "size_bytes": len(obj_bytes.getvalue())
            }
        )

        return obj_bytes.read()

    def _remove_background(self, image: Image.Image) -> Image.Image:
        """Remove background from image using rembg."""
        from rembg import remove

        # Remove background
        image_no_bg = remove(image)

        # Make background white instead of transparent
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image_no_bg, mask=image_no_bg.split()[3])

        return background

    async def generate_from_multiview(
        self,
        image_paths: list[str],
        mc_resolution: int = 256
    ) -> bytes:
        """
        Generate from multiple view images (better quality).

        Args:
            image_paths: List of image paths (4-8 views recommended)
            mc_resolution: Resolution

        Returns:
            OBJ file bytes
        """
        # For now, use first image
        # TODO: Implement actual multi-view fusion
        return await self.generate_from_image(
            image_paths[0],
            mc_resolution=mc_resolution
        )


# Singleton instance
_triposr_service: Optional[TripoSRService] = None

def get_triposr_service() -> TripoSRService:
    """Get TripoSR service singleton."""
    global _triposr_service
    if _triposr_service is None:
        import os
        model_path = os.getenv("TRIPOSR_MODEL_PATH", "/models/triposr")
        device = os.getenv("TRIPOSR_DEVICE", "cuda")
        _triposr_service = TripoSRService(model_path, device)
    return _triposr_service
```

### Usage Example

```python
from app.services.triposr import get_triposr_service

# Generate mesh from image
service = get_triposr_service()
obj_bytes = await service.generate_from_image(
    image_path="/path/to/chair.jpg",
    mc_resolution=256,
    remove_background=True
)

# Save to file
with open("chair.obj", "wb") as f:
    f.write(obj_bytes)
```

### Performance Optimization

```python
# GPU Memory Management
torch.cuda.empty_cache()  # Clear GPU memory after generation

# Batch Processing (if multiple images)
async def generate_batch_images(
    image_paths: list[str],
    batch_size: int = 4
) -> list[bytes]:
    """Process images in batches to optimize GPU usage."""
    results = []
    service = get_triposr_service()

    for i in range(0, len(image_paths), batch_size):
        batch = image_paths[i:i+batch_size]
        batch_results = await asyncio.gather(
            *[service.generate_from_image(path) for path in batch]
        )
        results.extend(batch_results)

        # Clear GPU memory between batches
        torch.cuda.empty_cache()

    return results
```

---

## 3. Pipeline Integration

### AI Pipeline Service

**File**: `backend/app/pipelines/ai.py`

```python
from __future__ import annotations

import logging
from typing import Optional
from app.services.shap_e import get_shap_e_service
from app.services.triposr import get_triposr_service
from app.services.mesh_processor import process_mesh
from app.services.mesh_converter import convert_mesh

logger = logging.getLogger("cadlift.pipeline.ai")

async def run_ai_pipeline(
    job_id: str,
    source_type: str,  # 'text' or 'image'
    source: str,  # prompt or image path
    params: dict
) -> dict:
    """
    Run AI generation pipeline.

    Returns:
        {
            "mesh_glb": bytes,
            "mesh_step": bytes,
            "mesh_dxf": bytes,
            "quality_metrics": dict,
            "metadata": dict
        }
    """
    logger.info(
        "Starting AI pipeline",
        extra={"job_id": job_id, "source_type": source_type}
    )

    # Generate mesh
    if source_type == "text":
        shap_e = get_shap_e_service()
        glb_bytes = await shap_e.generate_from_text(
            prompt=source,
            guidance_scale=params.get("guidance_scale", 15.0),
            num_steps=params.get("num_steps", 64)
        )
    elif source_type == "image":
        triposr = get_triposr_service()
        obj_bytes = await triposr.generate_from_image(
            image_path=source,
            mc_resolution=params.get("mc_resolution", 256)
        )
        # Convert OBJ to GLB
        glb_bytes = convert_mesh(obj_bytes, "obj", "glb")
    else:
        raise ValueError(f"Invalid source_type: {source_type}")

    # Process mesh (cleanup, repair, optimize)
    processed_mesh, quality_metrics = await process_mesh(
        glb_bytes,
        target_faces=params.get("target_faces", 50000),
        min_quality=params.get("min_quality", 7.0)
    )

    # Convert to other formats
    step_bytes = convert_mesh(processed_mesh, "glb", "step")
    dxf_bytes = convert_mesh(processed_mesh, "glb", "dxf")

    return {
        "mesh_glb": processed_mesh,
        "mesh_step": step_bytes,
        "mesh_dxf": dxf_bytes,
        "quality_metrics": quality_metrics,
        "metadata": {
            "pipeline": "ai",
            "source_type": source_type,
            "provider": "shap_e" if source_type == "text" else "triposr",
            "quality_score": quality_metrics["overall_score"]
        }
    }
```

---

## 4. Testing the Integration

### Unit Tests

```python
# tests/test_shap_e_integration.py

import pytest
from app.services.shap_e import get_shap_e_service

@pytest.mark.asyncio
async def test_shap_e_simple_object():
    """Test Shap-E generates simple object."""
    service = get_shap_e_service()

    if not service.enabled:
        pytest.skip("Shap-E not enabled")

    glb_bytes = await service.generate_from_text("a simple cube")

    assert len(glb_bytes) > 0
    assert glb_bytes[:4] == b"glTF"  # GLB magic number

@pytest.mark.asyncio
async def test_shap_e_organic_object():
    """Test Shap-E generates organic object."""
    service = get_shap_e_service()

    if not service.enabled:
        pytest.skip("Shap-E not enabled")

    glb_bytes = await service.generate_from_text("a detailed dragon")

    # Verify it's a valid GLB file
    mesh = trimesh.load(BytesIO(glb_bytes), file_type="glb")
    assert len(mesh.vertices) > 100
    assert len(mesh.faces) > 100
```

```python
# tests/test_triposr_integration.py

import pytest
from app.services.triposr import get_triposr_service

@pytest.mark.asyncio
async def test_triposr_chair():
    """Test TripoSR generates mesh from chair image."""
    service = get_triposr_service()

    # Use test image
    test_image = "tests/fixtures/chair.jpg"

    obj_bytes = await service.generate_from_image(
        image_path=test_image,
        mc_resolution=128  # Lower resolution for faster test
    )

    assert len(obj_bytes) > 0

    # Verify mesh
    mesh = trimesh.load(BytesIO(obj_bytes), file_type="obj")
    assert len(mesh.vertices) > 100
    assert len(mesh.faces) > 100
```

---

## 5. Monitoring & Analytics

### Metrics Collection

```python
from prometheus_client import Counter, Histogram

# Shap-E metrics
shap_e_calls = Counter(
    "shap_e_api_calls_total",
    "Total Shap-E API calls"
)
shap_e_errors = Counter(
    "shap_e_api_errors_total",
    "Total Shap-E API errors"
)
shap_e_duration = Histogram(
    "shap_e_duration_seconds",
    "Shap-E generation duration"
)

# TripoSR metrics
triposr_generations = Counter(
    "triposr_generations_total",
    "Total TripoSR generations"
)
triposr_duration = Histogram(
    "triposr_duration_seconds",
    "TripoSR generation duration"
)
```

### Cost Tracking

```python
# Track costs in database
INSERT INTO api_costs (
    job_id,
    provider,
    operation,
    cost,
    created_at
) VALUES (
    %s,  # job_id
    'shap_e',
    'text_to_3d',
    0.10,
    NOW()
);
```

---

## 6. Troubleshooting

### Common Issues

#### Shap-E API Key Invalid
```
Error: "Invalid API key"
Solution: Check OPENAI_API_KEY in .env file
```

#### TripoSR CUDA Out of Memory
```
Error: "CUDA out of memory"
Solutions:
1. Reduce mc_resolution (512 → 256 → 128)
2. Use CPU: TRIPOSR_DEVICE=cpu
3. Clear cache: torch.cuda.empty_cache()
```

#### Mesh Conversion Fails
```
Error: "Failed to convert GLB to STEP"
Solutions:
1. Check mesh is valid (watertight, manifold)
2. Run mesh repair first
3. Try alternative conversion method
```

---

## Next Steps

1. ✅ Set up OpenAI API key
2. ✅ Download TripoSR model
3. ✅ Implement Shap-E service
4. ✅ Implement TripoSR service
5. ✅ Test with simple objects
6. ✅ Integrate into pipeline
7. ✅ Add monitoring

---

**Integration Status**: 📋 **Ready for Implementation**
