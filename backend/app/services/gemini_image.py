"""
Gemini image generation service (text → image bytes).

Uses Google Gemini image models (e.g., gemini-2.5-flash-image) to create
reference images for downstream 3D generation (e.g., TripoSG).
"""
from __future__ import annotations

import logging
from typing import Optional
import base64
import requests

from app.core.config import get_settings

logger = logging.getLogger("cadlift.services.gemini_image")


class GeminiImageError(Exception):
    """Gemini image generation error."""


class GeminiImageService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.enabled = bool(self.settings.enable_gemini_triposg and self.settings.gemini_api_key)
        if not self.settings.gemini_api_key:
            logger.warning("Gemini image service disabled: GEMINI_API_KEY missing")
            self.enabled = False
        else:
            masked_key = f"{self.settings.gemini_api_key[:6]}...{self.settings.gemini_api_key[-4:]}" if self.settings.gemini_api_key else "none"
            logger.info(
                "Gemini image service initialized",
                extra={
                    "model": self.settings.gemini_image_model,
                    "fallback_model": self.settings.gemini_image_fallback_model,
                    "aspect_ratio": self.settings.gemini_image_aspect_ratio,
                    "resolution": self.settings.gemini_image_resolution,
                    "key": masked_key,
                },
            )

    def is_available(self) -> bool:
        return self.enabled

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None,
        model: Optional[str] = None,
    ) -> bytes:
        """
        Generate an image from text using Gemini.

        Returns:
            Image bytes (binary). Raises GeminiImageError on failure.
        """
        if not self.enabled:
            raise GeminiImageError("Gemini image service not enabled or missing API key.")

        try:
            primary = model or self.settings.gemini_image_model
            fallback = self.settings.gemini_image_fallback_model
            aspect = self.settings.gemini_image_aspect_ratio
            res = self.settings.gemini_image_resolution

            def _call(model_id: str):
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent"
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "responseModalities": ["IMAGE"],
                        "imageConfig": {
                            "aspectRatio": aspect,
                            "imageSize": res,
                        }
                    }
                }
                resp = requests.post(
                    url,
                    headers={
                        "Content-Type": "application/json",
                        "x-goog-api-key": self.settings.gemini_api_key or "",
                    },
                    json=payload,
                    timeout=60,
                )
                if resp.status_code == 429:
                    raise GeminiImageError(resp.text)
                if resp.status_code >= 400:
                    raise GeminiImageError(f"Gemini HTTP {resp.status_code}: {resp.text}")
                data = resp.json()
                cands = data.get("candidates") or []
                if not cands:
                    raise GeminiImageError("No candidates returned from Gemini.")
                parts = cands[0].get("content", {}).get("parts", []) or []
                for part in parts:
                    inline = part.get("inlineData") or part.get("inline_data") or None
                    if inline and inline.get("data"):
                        b64 = inline["data"]
                        try:
                            return base64.b64decode(b64)
                        except Exception:
                            return b64
                raise GeminiImageError("No image data found in Gemini response.")

            try:
                return _call(primary)
            except Exception as exc_primary:  # pragma: no cover
                if fallback and fallback != primary:
                    logger.warning(f"Gemini primary model failed ({primary}), trying fallback {fallback}: {exc_primary}")
                    return _call(fallback)
                raise

        except GeminiImageError:
            raise
        except Exception as exc:  # pragma: no cover - network/runtime errors
            logger.error(f"Gemini image generation failed: {exc}")
            raise GeminiImageError(str(exc))


_service: Optional[GeminiImageService] = None


def get_gemini_image_service() -> GeminiImageService:
    global _service
    if _service is None:
        _service = GeminiImageService()
    return _service
