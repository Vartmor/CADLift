"""
Local Stable Diffusion image generation service (text -> image bytes).

Uses Hugging Face diffusers to avoid paid API image calls. Intended to feed
TripoSR with a locally generated reference image. Falls back to disabled state
when dependencies or models are unavailable.
"""
from __future__ import annotations

import logging
from io import BytesIO
from typing import Optional

from app.core.config import get_settings

logger = logging.getLogger("cadlift.services.stable_diffusion")

try:  # optional dependency
    import torch  # type: ignore
    from diffusers import StableDiffusionPipeline  # type: ignore

    _SD_AVAILABLE = True
except ImportError:  # pragma: no cover
    _SD_AVAILABLE = False


class StableDiffusionError(Exception):
    """Stable Diffusion generation error."""


class StableDiffusionService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.enabled = bool(self.settings.enable_stable_diffusion)
        self.model_id = self.settings.stable_diffusion_model
        self.device = self.settings.stable_diffusion_device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.height = self.settings.stable_diffusion_height
        self.width = self.settings.stable_diffusion_width
        self.num_steps = self.settings.stable_diffusion_steps
        self.guidance = self.settings.stable_diffusion_guidance
        self._pipe: Optional[StableDiffusionPipeline] = None
        self._torch_dtype = torch.float16 if self.device.startswith("cuda") else torch.float32 if _SD_AVAILABLE else None

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
        return self.enabled

    def _ensure_pipeline(self) -> None:
        if self._pipe is not None:
            return
        try:
            pipe = StableDiffusionPipeline.from_pretrained(self.model_id, torch_dtype=self._torch_dtype)
            pipe.to(self.device)
            pipe.safety_checker = None  # disable NSFW filter for deterministic output
            self._pipe = pipe
        except Exception as exc:  # pragma: no cover - runtime/hardware issues
            logger.error("Failed to load Stable Diffusion pipeline", extra={"error": str(exc)})
            raise StableDiffusionError(f"Failed to load Stable Diffusion: {exc}")

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
