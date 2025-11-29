"""
Image-to-3D generation service using Shap-E image300M model.

Uses OpenAI's Shap-E image300M model (local, free) instead of TripoSR.
This provides better integration with our existing Shap-E pipeline.

Note: Originally planned to use TripoSR, but Shap-E image300M is simpler
and already part of our Shap-E installation (no additional dependencies!).
"""
from __future__ import annotations

import logging
from pathlib import Path
from io import BytesIO
from typing import Optional
import asyncio

logger = logging.getLogger("cadlift.services.image_to_3d")

# Shap-E imports (same as text-to-3D service)
try:
    import torch
    from PIL import Image
    from shap_e.diffusion.sample import sample_latents
    from shap_e.diffusion.gaussian_diffusion import diffusion_from_config
    from shap_e.models.download import load_model, load_config
    from shap_e.util.notebooks import decode_latent_mesh
    from shap_e.util.image_util import load_image as shap_e_load_image

    SHAP_E_AVAILABLE = True
except ImportError:
    SHAP_E_AVAILABLE = False


class TripoSRError(Exception):
    """Image-to-3D generation error."""


class TripoSRService:
    """
    Image-to-3D generation service using Shap-E image300M model.

    Despite the class name (kept for API compatibility), this uses Shap-E's
    image300M model for local, free image-to-3D generation.
    """

    def __init__(self, cache_dir: str | Path | None = None):
        self.cache_dir = Path(cache_dir) if cache_dir else Path(".cache/shap_e")
        self.image_model = None
        self.transmitter = None
        self.diffusion = None
        self.device = None

        if not SHAP_E_AVAILABLE:
            self.enabled = False
            logger.warning(
                "Image-to-3D service DISABLED - Shap-E not installed. "
                "Install from: cd docs/useful_projects/shap-e-main && pip install -e ."
            )
            return

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.enabled = True
        logger.info(
            "Image-to-3D service initialized (Shap-E image300M)",
            extra={"device": self.device.type},
        )

    def _load_model(self):
        """
        Lazy load the Shap-E image300M model.

        This downloads the model (~1.5GB) on first use.
        """
        if self.image_model is not None:
            return  # Already loaded

        if not SHAP_E_AVAILABLE:
            raise TripoSRError("Shap-E is not installed")

        self.cache_dir.mkdir(parents=True, exist_ok=True)

        try:
            logger.info("Loading Shap-E image300M model (first use - may take a few minutes)...")

            # Load transmitter (shared with text-to-3D)
            self.transmitter = load_model('transmitter', device=self.device)
            logger.info("✅ Loaded transmitter model")

            # Load image-to-3D diffusion model (300M parameters)
            self.image_model = load_model('image300M', device=self.device)
            logger.info("✅ Loaded image300M diffusion model")

            # Load diffusion config
            self.diffusion = diffusion_from_config(load_config('diffusion'))
            logger.info("✅ Loaded diffusion config")

            logger.info("🎉 Shap-E image300M model loaded successfully!")

        except Exception as exc:
            logger.error(f"Failed to load Shap-E image300M model: {exc}")
            raise TripoSRError(f"Failed to load image-to-3D model: {exc}") from exc

    def _load_image(self, image: str | Path | bytes) -> Image.Image:
        """Load and normalize an image input."""
        try:
            if isinstance(image, (str, Path)):
                return Image.open(image).convert("RGB")
            if isinstance(image, bytes):
                return Image.open(BytesIO(image)).convert("RGB")
            raise ValueError("Unsupported image input type")
        except Exception as exc:
            raise TripoSRError(f"Failed to load image: {exc}") from exc

    async def generate_from_image_async(
        self,
        image: str | Path | bytes,
        guidance_scale: float = 3.0,
        num_steps: int = 64,
    ) -> bytes:
        """
        Generate a mesh (PLY) from a single RGB image (async version).

        Args:
            image: Image path, bytes, or PIL Image
            guidance_scale: Classifier-free guidance (3.0 recommended for images)
            num_steps: Number of diffusion steps (64 recommended)

        Returns:
            PLY file bytes
        """
        if not self.enabled:
            raise TripoSRError("Image-to-3D service not enabled")

        self._load_model()
        pil_image = self._load_image(image)

        logger.info(
            "Generating 3D from image with Shap-E image300M",
            extra={
                "image_size": pil_image.size,
                "guidance_scale": guidance_scale,
                "num_steps": num_steps,
            }
        )

        try:
            # Run in thread pool to avoid blocking event loop
            loop = asyncio.get_event_loop()
            ply_bytes = await loop.run_in_executor(
                None,
                self._generate_mesh_sync,
                pil_image,
                guidance_scale,
                num_steps
            )

            logger.info(
                "Image-to-3D generation successful",
                extra={"output_size_bytes": len(ply_bytes)},
            )
            return ply_bytes

        except Exception as exc:
            logger.error(f"Image-to-3D generation failed: {exc}")
            raise TripoSRError(f"Failed to generate mesh from image: {exc}") from exc

    def generate_from_image(
        self,
        image: str | Path | bytes,
        guidance_scale: float = 3.0,
        num_steps: int = 64,
    ) -> bytes:
        """
        Generate a mesh (PLY) from a single RGB image (sync wrapper).

        This is a synchronous wrapper for compatibility. Use generate_from_image_async
        for better async/await support.

        Returns:
            PLY file bytes (convert to OBJ/GLB with mesh_converter)
        """
        # Run async version in new event loop
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                self.generate_from_image_async(image, guidance_scale, num_steps)
            )
        finally:
            loop.close()

    def _generate_mesh_sync(
        self,
        pil_image: Image.Image,
        guidance_scale: float,
        num_steps: int
    ) -> bytes:
        """
        Synchronous mesh generation from image (runs in thread pool).

        This uses Shap-E's image300M model for local image-to-3D generation.
        """
        try:
            # Sample latents using diffusion with image conditioning
            batch_size = 1
            latents = sample_latents(
                batch_size=batch_size,
                model=self.image_model,
                diffusion=self.diffusion,
                guidance_scale=guidance_scale,
                model_kwargs=dict(images=[pil_image] * batch_size),
                progress=True,
                clip_denoised=True,
                use_fp16=True,
                use_karras=True,
                karras_steps=num_steps,
                sigma_min=1e-3,
                sigma_max=160,
                s_churn=0,
            )

            logger.info(f"✅ Generated {len(latents)} latent(s) from image")

            # Decode latent to mesh
            latent = latents[0]
            mesh = decode_latent_mesh(self.transmitter, latent).tri_mesh()

            logger.info(f"✅ Decoded mesh: {len(mesh.verts)} vertices, {len(mesh.faces)} faces")

            # Export to PLY format
            ply_stream = BytesIO()
            mesh.write_ply(ply_stream)
            ply_bytes = ply_stream.getvalue()

            logger.info(f"✅ Exported PLY: {len(ply_bytes)} bytes")

            return ply_bytes

        except Exception as e:
            logger.error(f"Mesh generation from image failed: {e}")
            raise TripoSRError(f"Local image-to-3D generation failed: {e}")


# Singleton
_triposr_service: Optional[TripoSRService] = None


def get_triposr_service() -> TripoSRService:
    """Get image-to-3D service singleton."""
    global _triposr_service
    if _triposr_service is None:
        _triposr_service = TripoSRService()
    return _triposr_service


# Convenience functions
async def generate_from_image(
    image: str | Path | bytes,
    guidance_scale: float = 3.0,
    num_steps: int = 64
) -> bytes:
    """
    Generate 3D mesh from image.

    Args:
        image: Image path, bytes, or PIL Image
        guidance_scale: Classifier-free guidance (3.0 for images)
        num_steps: Diffusion steps (64 recommended)

    Returns:
        PLY file bytes
    """
    service = get_triposr_service()
    return await service.generate_from_image_async(image, guidance_scale, num_steps)
