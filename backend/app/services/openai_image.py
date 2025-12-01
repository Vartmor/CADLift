"""
OpenAI image generation service (text → image bytes).

Uses OpenAI Image API (gpt-image-1 by default) to generate a reference image
for downstream 3D reconstruction (e.g., TripoSG).
"""
from __future__ import annotations

import base64
import logging
from typing import Optional

from app.core.config import get_settings

logger = logging.getLogger("cadlift.services.openai_image")

try:  # optional dependency
    from openai import OpenAI  # type: ignore
    _OPENAI_AVAILABLE = True
except ImportError:  # pragma: no cover
    _OPENAI_AVAILABLE = False


class OpenAIImageError(Exception):
    """OpenAI image generation error."""


class OpenAIImageService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.enabled = bool(self.settings.openai_api_key and self.settings.enable_gemini_triposg)
        if not self.settings.openai_api_key:
            logger.warning("OpenAI image service disabled: OPENAI_API_KEY missing")
            self.enabled = False
            return
        if not _OPENAI_AVAILABLE:
            logger.warning("OpenAI image service disabled: openai package not installed")
            self.enabled = False
            return

        masked_key = f"{self.settings.openai_api_key[:6]}...{self.settings.openai_api_key[-4:]}"
        logger.info(
            "OpenAI image service initialized",
            extra={
                "model": "gpt-image-1",
                "size": "1024x1024",
                "quality": "high",
                "key": masked_key,
            },
        )

    def is_available(self) -> bool:
        return self.enabled

    def generate_image(
        self,
        prompt: str,
        *,
        size: str = "1024x1024",
        quality: str = "high",
        model: str = "gpt-image-1",
    ) -> bytes:
        """
        Generate an image from text using OpenAI Image API.

        Returns:
            Image bytes.
        """
        if not self.enabled:
            raise OpenAIImageError("OpenAI image service not enabled or missing dependencies.")

        try:
            client = OpenAI(api_key=self.settings.openai_api_key)
            result = client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
            )
            data = result.data or []
            if not data:
                raise OpenAIImageError("No image data returned from OpenAI.")
            b64 = data[0].b64_json
            if not b64:
                raise OpenAIImageError("Empty image payload from OpenAI.")
            return base64.b64decode(b64)
        except Exception as exc:  # pragma: no cover - network/runtime errors
            logger.error(f"OpenAI image generation failed: {exc}")
            raise OpenAIImageError(str(exc))


_service: Optional[OpenAIImageService] = None


def get_openai_image_service() -> OpenAIImageService:
    global _service
    if _service is None:
        _service = OpenAIImageService()
    return _service
