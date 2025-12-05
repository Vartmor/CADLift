"""
Local Stable Diffusion image generation service (text -> image bytes).

Uses Hugging Face diffusers to avoid paid API image calls. Intended to feed
TripoSR with a locally generated reference image. Falls back to disabled state
when dependencies or models are unavailable.
"""
from __future__ import annotations

import logging
import gc
from io import BytesIO
from typing import Optional, Any

from app.core.config import get_settings

logger = logging.getLogger("cadlift.services.stable_diffusion")

# Optional dependencies - must check before using
_SD_AVAILABLE = False
_torch = None
_StableDiffusionPipeline = None

try:
    import torch as _torch_module
    from diffusers import StableDiffusionPipeline as _SDPipeline

    _torch = _torch_module
    _StableDiffusionPipeline = _SDPipeline
    _SD_AVAILABLE = True
except ImportError:  # pragma: no cover
    pass


def _get_device() -> str:
    """Safely get the best available device."""
    if not _SD_AVAILABLE or _torch is None:
        return "cpu"
    try:
        return "cuda" if _torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


def _get_torch_dtype(device: str) -> Any:
    """Safely get the appropriate torch dtype for the device."""
    if not _SD_AVAILABLE or _torch is None:
        return None
    try:
        return _torch.float16 if device.startswith("cuda") else _torch.float32
    except Exception:
        return None


class StableDiffusionError(Exception):
    """Stable Diffusion generation error."""


class StableDiffusionService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.enabled = bool(self.settings.enable_stable_diffusion)
        self.model_id = self.settings.stable_diffusion_model
        self.height = self.settings.stable_diffusion_height
        self.width = self.settings.stable_diffusion_width
        self.num_steps = self.settings.stable_diffusion_steps
        self.guidance = self.settings.stable_diffusion_guidance
        self._pipe: Any = None
        
        # Initialize device and dtype safely
        self.device = self.settings.stable_diffusion_device or _get_device()
        self._torch_dtype = _get_torch_dtype(self.device)

        if not _SD_AVAILABLE:
            logger.warning("Stable Diffusion service disabled: diffusers/torch not installed")
            self.enabled = False
            return

        masked_model = self.model_id if len(self.model_id) < 12 else f"{self.model_id[:8]}..."
        logger.info(
            "Stable Diffusion service configured",
            extra={
                "model": masked_model,
                "device": self.device,
                "height": self.height,
                "width": self.width,
                "steps": self.num_steps,
            },
        )

    def is_available(self) -> bool:
        return self.enabled and _SD_AVAILABLE

    def _ensure_pipeline(self) -> None:
        if self._pipe is not None:
            return
        if not _SD_AVAILABLE or _StableDiffusionPipeline is None:
            raise StableDiffusionError("Stable Diffusion dependencies not installed")
        
        try:
            logger.info("Loading Stable Diffusion model (this may take a few minutes on first run)...")
            
            # Load model - HuggingFace will use cache if available
            pipe = _StableDiffusionPipeline.from_pretrained(
                self.model_id, 
                torch_dtype=self._torch_dtype,
                safety_checker=None,
                requires_safety_checker=False,
            )
            
            logger.info("Model loaded, applying optimizations...")
            
            # Memory optimizations for CUDA
            if self.device.startswith("cuda") and _torch is not None:
                try:
                    # Log VRAM info
                    try:
                        props = _torch.cuda.get_device_properties(0)
                        total_vram_gb = props.total_memory / (1024**3)
                        logger.info(f"GPU: {props.name}, Total VRAM: {total_vram_gb:.1f} GB")
                    except Exception:
                        pass
                    
                    # Enable memory-efficient attention
                    if hasattr(pipe, 'enable_attention_slicing'):
                        pipe.enable_attention_slicing("auto")
                        logger.info("Enabled attention slicing")
                    
                    # Enable VAE slicing for large images
                    if hasattr(pipe, 'enable_vae_slicing'):
                        pipe.enable_vae_slicing()
                        logger.info("Enabled VAE slicing")
                        
                except Exception as e:
                    logger.warning(f"Memory optimization failed (non-critical): {e}")
            
            # Move to device
            logger.info(f"Moving model to device: {self.device}")
            pipe.to(self.device)
            self._pipe = pipe
            logger.info("Stable Diffusion model loaded successfully")
            
        except Exception as exc:  # pragma: no cover
            logger.error("Failed to load Stable Diffusion pipeline", extra={"error": str(exc)})
            raise StableDiffusionError(f"Failed to load Stable Diffusion: {exc}")

    def unload(self) -> None:
        """Unload the model to free memory for other services."""
        if self._pipe is not None:
            del self._pipe
            self._pipe = None
            if _torch is not None:
                try:
                    _torch.cuda.empty_cache()
                except Exception:
                    pass
            gc.collect()
            logger.info("Stable Diffusion model unloaded")

    def generate_image(
        self,
        prompt: str,
        *,
        height: Optional[int] = None,
        width: Optional[int] = None,
        num_inference_steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        negative_prompt: Optional[str] = None,
    ) -> bytes:
        if not self.enabled:
            raise StableDiffusionError("Stable Diffusion service not enabled.")

        self._ensure_pipeline()
        assert self._pipe is not None

        h = height or self.height
        w = width or self.width
        steps = num_inference_steps or self.num_steps
        guidance = guidance_scale or self.guidance

        logger.info(f"Generating image: {prompt[:50]}... ({w}x{h}, {steps} steps)")

        try:
            result = self._pipe(
                prompt=prompt,
                height=h,
                width=w,
                num_inference_steps=steps,
                guidance_scale=guidance,
                negative_prompt=negative_prompt,
            )
            images = result.images or []
            if not images:
                raise StableDiffusionError("No image returned from Stable Diffusion.")
            img = images[0]
            buf = BytesIO()
            img.save(buf, format="PNG")
            logger.info("Image generation complete")
            return buf.getvalue()
        except Exception as exc:  # pragma: no cover
            logger.error("Stable Diffusion generation failed", extra={"error": str(exc)})
            raise StableDiffusionError(str(exc))


_service: Optional[StableDiffusionService] = None


def get_stable_diffusion_service() -> StableDiffusionService:
    global _service
    if _service is None:
        _service = StableDiffusionService()
    return _service

