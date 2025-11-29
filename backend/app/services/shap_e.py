"""
OpenAI Shap-E text-to-3D generation service.

Using LOCAL Shap-E models from docs/useful_projects/shap-e-main
- No API costs!
- No rate limits!
- Full privacy!

Models used:
- text300M: Text-to-3D diffusion model (300M parameters)
- image300M: Image-to-3D diffusion model (Phase 2)
- transmitter: Encoder/decoder for mesh generation
"""
from __future__ import annotations

import asyncio
import logging
from typing import Optional
import os
from io import BytesIO

# Local Shap-E imports (install from docs/useful_projects/shap-e-main)
try:
    import torch
    from shap_e.diffusion.sample import sample_latents
    from shap_e.diffusion.gaussian_diffusion import diffusion_from_config
    from shap_e.models.download import load_model, load_config
    from shap_e.util.notebooks import decode_latent_mesh
    SHAP_E_AVAILABLE = True
except ImportError:
    SHAP_E_AVAILABLE = False
    # Will log warning in __init__

logger = logging.getLogger("cadlift.services.shap_e")


class ShapEAPIError(Exception):
    """Shap-E API error."""
    pass


class ShapEService:
    """OpenAI Shap-E text-to-3D generation service using LOCAL models."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = "shap-e"  # Local Shap-E models (no API costs)
        self.device = None
        self.shap_e_model = None
        self.transmitter = None
        self.diffusion = None

        # Check if Shap-E is available
        if not SHAP_E_AVAILABLE:
            self.enabled = False
            logger.warning(
                "Shap-E service DISABLED - shap_e package not installed. "
                "Install from: cd docs/useful_projects/shap-e-main && pip install -e ."
            )
        else:
            self.enabled = True
            # Detect device (GPU if available, else CPU)
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

            if self.device.type == 'cuda':
                logger.info(f"Shap-E service initialized with GPU acceleration ({torch.cuda.get_device_name(0)})")
            else:
                logger.info("Shap-E service initialized with CPU (slower, ~2-5 min per object)")

            logger.info(
                "Shap-E service ready - using LOCAL models (FREE, no API costs!)"
            )

    def _load_models(self):
        """
        Lazy load Shap-E models (only on first generation).

        Models are auto-downloaded from OpenAI on first use (~4GB).
        """
        if self.shap_e_model is not None:
            return  # Already loaded

        logger.info("Loading Shap-E models (first use - may take a few minutes)...")

        try:
            # Load transmitter (encoder/decoder)
            self.transmitter = load_model('transmitter', device=self.device)
            logger.info("✅ Loaded transmitter model")

            # Load text-to-3D diffusion model (300M parameters)
            self.shap_e_model = load_model('text300M', device=self.device)
            logger.info("✅ Loaded text300M diffusion model")

            # Load diffusion config
            self.diffusion = diffusion_from_config(load_config('diffusion'))
            logger.info("✅ Loaded diffusion config")

            logger.info("🎉 All Shap-E models loaded successfully!")

        except Exception as e:
            logger.error(f"Failed to load Shap-E models: {e}")
            self.enabled = False
            raise ShapEAPIError(f"Failed to load Shap-E models: {e}")

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
            guidance_scale: Classifier-free guidance scale (higher = more faithful to prompt)
            num_steps: Number of diffusion steps (higher = better quality, slower)
            frame_size: Output resolution (64, 128, 256)

        Returns:
            PLY file bytes (convert to GLB/STEP/DXF with mesh_converter)

        Raises:
            ShapEAPIError: If generation fails or service not enabled
        """
        if not self.enabled:
            raise ShapEAPIError(
                "Shap-E service not enabled. Install from docs/useful_projects/shap-e-main with pip install -e ."
            )

        # Optimize prompt
        optimized_prompt = self._optimize_prompt(prompt)

        logger.info(
            "Generating 3D from text with Shap-E",
            extra={
                "prompt": prompt[:100],
                "optimized": optimized_prompt[:100],
                "guidance_scale": guidance_scale,
                "num_steps": num_steps,
            }
        )

        try:
            # TODO: Replace with actual Shap-E API call when available
            # For now, this is a placeholder that demonstrates the interface

            mesh_bytes = await self._call_shap_e_api(
                optimized_prompt,
                guidance_scale,
                num_steps,
                frame_size
            )

            logger.info(
                "Shap-E generation successful",
                extra={"size_bytes": len(mesh_bytes)}
            )

            return mesh_bytes

        except Exception as e:
            logger.error(f"Shap-E generation failed: {e}")
            raise ShapEAPIError(f"Failed to generate 3D mesh: {e}")

    async def _call_shap_e_api(
        self,
        prompt: str,
        guidance_scale: float,
        num_steps: int,
        frame_size: int
    ) -> bytes:
        """
        Generate 3D mesh using LOCAL Shap-E models.

        This runs on your server (GPU/CPU) - no API calls, no costs!

        Args:
            prompt: Optimized text prompt
            guidance_scale: Classifier-free guidance scale (15.0 recommended)
            num_steps: Diffusion steps (64 recommended)
            frame_size: Output resolution (not used in local generation)

        Returns:
            PLY file bytes (can be converted to GLB/STEP/DXF)
        """
        # Load models on first use
        self._load_models()

        logger.info(f"Generating 3D mesh locally with Shap-E on {self.device.type}...")

        # Run in thread pool to avoid blocking event loop
        loop = asyncio.get_event_loop()
        mesh_bytes = await loop.run_in_executor(
            None,
            self._generate_mesh_sync,
            prompt,
            guidance_scale,
            num_steps
        )

        return mesh_bytes

    def _generate_mesh_sync(
        self,
        prompt: str,
        guidance_scale: float,
        num_steps: int
    ) -> bytes:
        """
        Synchronous mesh generation (runs in thread pool).

        This is the actual Shap-E generation code based on the official examples.
        """
        try:
            # Sample latents using diffusion
            batch_size = 1  # Generate one object at a time
            latents = sample_latents(
                batch_size=batch_size,
                model=self.shap_e_model,
                diffusion=self.diffusion,
                guidance_scale=guidance_scale,
                model_kwargs=dict(texts=[prompt] * batch_size),
                progress=True,
                clip_denoised=True,
                use_fp16=True,
                use_karras=True,
                karras_steps=num_steps,
                sigma_min=1e-3,
                sigma_max=160,
                s_churn=0,
            )

            logger.info(f"✅ Generated {len(latents)} latent(s)")

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
            logger.error(f"Mesh generation failed: {e}")
            raise ShapEAPIError(f"Local mesh generation failed: {e}")

    def _optimize_prompt(self, prompt: str) -> str:
        """
        Optimize prompt for better Shap-E results.

        Strategies:
        - Add "3D model of" prefix if missing
        - Add quality keywords: "detailed", "high-quality"
        - Remove ambiguous terms
        - Simplify complex descriptions
        """
        optimized = prompt.lower().strip()

        # Add 3D context if missing
        if "3d" not in optimized and "model" not in optimized:
            optimized = f"3D model of {optimized}"

        # Add quality keywords if missing
        if "detailed" not in optimized and "quality" not in optimized and "realistic" not in optimized:
            optimized = f"detailed {optimized}"

        # Capitalize properly
        optimized = optimized[0].upper() + optimized[1:] if optimized else optimized

        logger.debug(f"Prompt optimized: '{prompt}' → '{optimized}'")

        return optimized

    async def generate_batch(
        self,
        prompts: list[str],
        max_concurrent: int = 3
    ) -> list[bytes | None]:
        """
        Generate multiple meshes in batch with concurrency control.

        Args:
            prompts: List of text prompts
            max_concurrent: Max simultaneous API calls

        Returns:
            List of GLB bytes (same order as prompts), None for failed generations
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def generate_one(prompt: str) -> bytes | None:
            async with semaphore:
                try:
                    return await self.generate_from_text(prompt)
                except Exception as e:
                    logger.error(f"Batch generation failed for '{prompt}': {e}")
                    return None

        results = await asyncio.gather(
            *[generate_one(p) for p in prompts],
            return_exceptions=False
        )

        return results


# Cost tracking
class ShapECostTracker:
    """Track Shap-E generation calls (local = $0.00)."""

    COST_PER_CALL = 0.0  # Local models: free!

    def __init__(self):
        self.total_calls = 0
        self.total_cost = 0.0

    def record_call(self, prompt: str):
        """Record a Shap-E generation call."""
        self.total_calls += 1
        self.total_cost += self.COST_PER_CALL

        logger.info(
            "Shap-E generation tracked (local, no API cost)",
            extra={
                "total_calls": self.total_calls,
                "total_cost": f"${self.total_cost:.2f}",
                "prompt": prompt[:50]
            }
        )

    def check_budget(self, monthly_budget: float = 500.0) -> bool:
        """Check if within budget."""
        return self.total_cost < monthly_budget


# Error handling & retry
async def generate_with_retry(
    prompt: str,
    max_retries: int = 3,
    service: ShapEService | None = None
) -> bytes:
    """Generate with automatic retry on failure."""
    if service is None:
        service = get_shap_e_service()

    for attempt in range(max_retries):
        try:
            return await service.generate_from_text(prompt)

        except ShapEAPIError as e:
            logger.warning(
                f"Shap-E attempt {attempt + 1}/{max_retries} failed: {e}",
                extra={"prompt": prompt[:50]}
            )

            if attempt == max_retries - 1:
                raise

            # Exponential backoff
            await asyncio.sleep(2 ** attempt)

    raise ShapEAPIError("All retry attempts failed")


# Singleton
_shap_e_service: Optional[ShapEService] = None
_cost_tracker: Optional[ShapECostTracker] = None


def get_shap_e_service() -> ShapEService:
    """Get Shap-E service singleton."""
    global _shap_e_service
    if _shap_e_service is None:
        _shap_e_service = ShapEService()
    return _shap_e_service


def get_cost_tracker() -> ShapECostTracker:
    """Get cost tracker singleton."""
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = ShapECostTracker()
    return _cost_tracker
