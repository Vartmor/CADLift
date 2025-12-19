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
import gc
import logging
from pathlib import Path
from io import BytesIO
from typing import Optional, Any
import numpy as np

logger = logging.getLogger("cadlift.services.triposr")

# Check if TripoSR is available (opt-in; avoids hard crashes on missing native deps)
TRIPOSR_AVAILABLE = False
_torch = None
_TSR = None
_remove_background = None
_resize_foreground = None
_Image = None  # PIL Image

if os.environ.get("TRIPOSR_DISABLE", "0") != "1":
    _triposr_path = Path(__file__).parent.parent.parent.parent / "vendor" / "triposr"
    try:
        from PIL import Image as _PILImage
        _Image = _PILImage
        
        import torch as _torch_module
        _torch = _torch_module
        
        if _triposr_path.exists():
            sys.path.insert(0, str(_triposr_path))
            from tsr.system import TSR as _TSR_class
            from tsr.utils import remove_background as _rb, resize_foreground as _rf
            _TSR = _TSR_class
            _remove_background = _rb
            _resize_foreground = _rf
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


def _get_optimal_resolution() -> int:
    """Determine optimal marching cubes resolution based on available memory."""
    if _torch is None:
        return 128  # Conservative default
    
    try:
        if _torch.cuda.is_available():
            # Check GPU memory
            props = _torch.cuda.get_device_properties(0)
            total_mem = props.total_memory / (1024**3)  # GB
            
            if total_mem >= 12:
                return 256  # High quality for 12GB+ GPUs
            elif total_mem >= 8:
                return 192  # Medium-high for 8GB GPUs
            elif total_mem >= 6:
                return 160  # Medium for 6GB GPUs
            else:
                return 128  # Low for 4GB GPUs
        else:
            # CPU mode - check system RAM
            import psutil
            ram_gb = psutil.virtual_memory().total / (1024**3)
            if ram_gb >= 32:
                return 192
            elif ram_gb >= 16:
                return 160
            else:
                return 128
    except Exception:
        return 128


class TripoSRService:
    """TripoSR image-to-3D service."""

    def __init__(self):
        self.enabled = False
        self.model = None
        self.device = None
        self._loaded = False
        self.mc_resolution = _get_optimal_resolution()

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

        if _torch is not None:
            self.device = _torch.device('cuda' if _torch.cuda.is_available() else 'cpu')
        else:
            self.device = "cpu"
        
        logger.info(f"TripoSR service initialized (device: {self.device}, resolution: {self.mc_resolution})")

    def is_available(self) -> bool:
        """Check if TripoSR service is available."""
        return self.enabled and TRIPOSR_AVAILABLE

    def _ensure_loaded(self):
        if not self.enabled:
            raise TripoSRError("TripoSR service not enabled; install dependencies and clone docs/useful_projects/TripoSR")
        if self._loaded:
            return
        
        if _TSR is None:
            raise TripoSRError("TripoSR TSR class not available")
        
        # CRITICAL: Aggressive GPU cleanup before loading model
        # This prevents crashes when other models (SD) were recently using GPU
        if _torch is not None and _torch.cuda.is_available():
            try:
                logger.info("Clearing GPU memory before loading TripoSR...")
                _torch.cuda.empty_cache()
                _torch.cuda.synchronize()  # Wait for any pending ops
                gc.collect()
                
                # Force a lower resolution for safety
                self.mc_resolution = min(self.mc_resolution, 128)
                logger.info(f"Using safe resolution: {self.mc_resolution}")
            except Exception as e:
                logger.warning(f"GPU cleanup failed: {e}")
            
        try:
            logger.info("Loading TripoSR model (this may take a minute on first run)...")
            
            # Prefer local repo weights; if unavailable, try HF download
            self.model = _TSR.from_pretrained(
                "stabilityai/TripoSR",
                config_name="config.yaml",
                weight_name="model.ckpt",
            )
            
            # Reduce memory for small GPUs
            if hasattr(self.model, "renderer"):
                try:
                    self.model.renderer.set_chunk_size(512)  # Even smaller chunks for safety
                    logger.info("Set renderer chunk size to 512 for memory efficiency")
                except Exception:
                    pass
                    
            self.model.to(self.device)
            self.model.eval()
            self._loaded = True
            logger.info("TripoSR model loaded successfully")
            
        except Exception as exc:
            logger.error(f"Failed to load TripoSR model: {exc}")
            raise TripoSRError(f"Failed to load TripoSR model: {exc}")

    def unload(self) -> None:
        """Unload the model to free GPU memory."""
        if self.model is not None:
            del self.model
            self.model = None
            self._loaded = False
            
            if _torch is not None:
                try:
                    _torch.cuda.empty_cache()
                except Exception:
                    pass
            gc.collect()
            logger.info("TripoSR model unloaded")

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

        if _torch is None:
            raise TripoSRError("PyTorch not available")

        self._ensure_loaded()

        try:
            logger.info("Preprocessing image for 3D reconstruction...")
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
            
            if bg_removal and _remove_background is not None and _resize_foreground is not None:
                # Match upstream TripoSR preprocessing: remove BG, crop to foreground,
                # composite over gray background, keep 3 channels.
                logger.info("Removing background...")
                image = _remove_background(image)
                image = image.convert("RGBA")
                image = _resize_foreground(image, ratio=foreground_ratio)
                arr = np.array(image).astype(np.float32) / 255.0
                arr = arr[..., :3] * arr[..., 3:4] + (1 - arr[..., 3:4]) * 0.5
                image = Image.fromarray((arr * 255.0).astype(np.uint8))
            else:
                arr = np.array(image).astype(np.float32) / 255.0
                image = Image.fromarray((arr * 255.0).astype(np.uint8))

            logger.info(f"Generating 3D mesh (resolution: {self.mc_resolution})...")
            
            with _torch.inference_mode():
                scene_codes = self.model([image], device=self.device)
                meshes = self.model.extract_mesh(
                    scene_codes,
                    has_vertex_color=False,
                    resolution=self.mc_resolution,
                )
                mesh = meshes[0]
                
            buf = BytesIO()
            mesh.export(buf, file_type="obj")
            
            logger.info("3D mesh generation complete")
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

