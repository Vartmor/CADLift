from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger("cadlift.vision")
settings = get_settings()


class VisionService:
    def __init__(self, api_url: str | None, api_key: str | None, timeout_seconds: float = 30.0):
        self.api_url = api_url
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    @property
    def enabled(self) -> bool:
        return bool(self.api_url and self.api_key)

    async def vectorize(self, image_path: Path) -> list[list[list[float]]]:
        if not self.enabled:
            raise RuntimeError("Vision service not enabled")
        headers = {"Authorization": f"Bearer {self.api_key}"}
        files = {"file": image_path.open("rb")}
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(f"{self.api_url}/vectorize", headers=headers, files=files)
            response.raise_for_status()
            data: dict[str, Any] = response.json()
        polygons = data.get("polygons")
        if not isinstance(polygons, list):
            raise ValueError("Vision API response missing polygons")
        validated: list[list[list[float]]] = []
        for poly in polygons:
            if not isinstance(poly, list):
                continue
            pts: list[list[float]] = []
            for pt in poly:
                if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                    pts.append([float(pt[0]), float(pt[1])])
            if len(pts) >= 3:
                validated.append(pts)
        if not validated:
            raise ValueError("Vision API returned no valid polygons")
        logger.info(
            "Vision API vectorized image",
            extra={
                "polygon_count": len(validated),
                "api_url": self.api_url,
            },
        )
        return validated


vision_service = VisionService(
    api_url=getattr(settings, "vision_api_url", None),
    api_key=getattr(settings, "vision_api_key", None),
    timeout_seconds=getattr(settings, "vision_timeout_seconds", 30.0),
)
