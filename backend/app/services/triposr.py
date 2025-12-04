"""
TripoSR service for image-to-3D generation.

TripoSR is a fast image-to-3D reconstruction model from Stability AI.
Replaces Shap-E which had PyTorch/CLIP compatibility issues on Windows.

Features:
- Image-to-3D mesh generation (<30s on GPU, <2min on CPU)
- No CLIP dependency (avoids JIT loading bug)
- Modern architecture (2024)
- Perfect for engineering drawings and CAD objects
"""
from __future__ import annotations

import os
import sys
import logging
from pathlib import Path
from io import BytesIO
from typing import Optional
import numpy as np
from PIL import Image

logger = logging.getLogger("cadlift.services.triposr")

# Check if TripoSR is available (opt-in; avoids hard crashes on missing native deps)
TRIPOSR_AVAILABLE = False
if os.environ.get("TRIPOSR_DISABLE", "0") != "1":
    _triposr_path = Path(__file__).parent.parent.parent.parent / "docs" / "useful_projects" / "TripoSR"
    try:
        import torch
        if _triposr_path.exists():
            sys.path.insert(0, str(_triposr_path))
            from tsr.system import TSR
            from tsr.utils import remove_background, resize_foreground
            TRIPOSR_AVAILABLE = True
            logger.info(f"TripoSR module found at {_triposr_path}")
        else:
            logger.warning(f"TripoSR not found at {_triposr_path}")
    except ImportError as e:
        logger.warning(f"TripoSR dependencies not available: {e}")
else:
    logger.info("TRIPOSR_DISABLE=1 -> TripoSR service disabled at import time")


class TripoSRError(Exception):
    """TripoSR generation error."""
    pass


class TripoSRService:
    """TripoSR image-to-3D service."""

    def __init__(self):
        self.enabled = False
        self.model = None
        self.device = None
        self._loaded = False
        self.mc_resolution = 128  # lower resolution to fit 4GB GPUs

        if not TRIPOSR_AVAILABLE:
            logger.warning("TripoSR service DISABLED - dependencies not available")
            return

        try:
            import omegaconf
            import einops
            import transformers
            self.enabled = True
        except ImportError as e:
            logger.warning(f"TripoSR service DISABLED - missing dependencies: {e}")
            return

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"TripoSR service initialized (device: {self.device})")

    def is_available(self) -> bool:
        """Check if TripoSR service is available."""
        return self.enabled

    def _ensure_loaded(self):
        if not self.enabled:
            raise TripoSRError("TripoSR service not enabled; install dependencies and clone docs/useful_projects/TripoSR")
        if self._loaded:
            return
        try:
            # Prefer local repo weights; if unavailable, try HF download
            self.model = TSR.from_pretrained(
                "stabilityai/TripoSR",
                config_name="config.yaml",
                weight_name="model.ckpt",
            )
            # reduce memory for small GPUs
            if hasattr(self.model, "renderer"):
                try:
                    self.model.renderer.set_chunk_size(1024)
                except Exception:
                    pass
            self.model.to(self.device)
            self.model.eval()
            self._loaded = True
            logger.info("TripoSR model loaded")
        except Exception as exc:
            logger.error(f"Failed to load TripoSR model: {exc}")
            raise TripoSRError(f"Failed to load TripoSR model: {exc}")

    # Backwards-compatibility helpers expected by tests
    def _load_model(self):
        """Load and return the underlying TSR model."""
        self._ensure_loaded()
        return self.model

    def _load_image(self, image_bytes: bytes) -> Image.Image:
        """Load image bytes into a PIL Image."""
        try:
            return Image.open(BytesIO(image_bytes)).convert("RGB")
        except Exception as exc:  # noqa: BLE001
            raise TripoSRError(f"Failed to load image bytes: {exc}") from exc

    def generate_from_image(self, image_bytes: bytes, bg_removal: bool = True, foreground_ratio: float = 0.85) -> bytes:
        """
        Generate 3D mesh (OBJ) from a single image.

        Args:
            image_bytes: Input image bytes (PNG/JPG)
            bg_removal: Whether to remove background before reconstruction
            foreground_ratio: Resize ratio for foreground cropping

        Returns:
            OBJ file bytes

        Raises:
            TripoSRError: if generation fails or service not available
        """
        if not self.enabled:
            raise TripoSRError("TripoSR service not enabled; install dependencies.")

        self._ensure_loaded()

        try:
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
            if bg_removal:
                # Match upstream TripoSR preprocessing: remove BG, crop to foreground,
                # composite over gray background, keep 3 channels.
                image = remove_background(image)
                image = image.convert("RGBA")
                image = resize_foreground(image, ratio=foreground_ratio)
                arr = np.array(image).astype(np.float32) / 255.0
                arr = arr[..., :3] * arr[..., 3:4] + (1 - arr[..., 3:4]) * 0.5
                image = Image.fromarray((arr * 255.0).astype(np.uint8))
            else:
                arr = np.array(image).astype(np.float32) / 255.0
                image = Image.fromarray((arr * 255.0).astype(np.uint8))

            with torch.inference_mode():
                scene_codes = self.model([image], device=self.device)
                meshes = self.model.extract_mesh(
                    scene_codes,
                    has_vertex_color=False,
                    resolution=self.mc_resolution,
                )
                mesh = meshes[0]
            buf = BytesIO()
            mesh.export(buf, file_type="obj")
            return buf.getvalue()
        except Exception as exc:
            logger.exception("TripoSR generation failed")
            raise TripoSRError(f"TripoSR generation failed: {exc}")


# Singleton
_triposr_service: Optional[TripoSRService] = None


def get_triposr_service() -> TripoSRService:
    """Get TripoSR service singleton."""
    global _triposr_service
    if _triposr_service is None:
        _triposr_service = TripoSRService()
    return _triposr_service
