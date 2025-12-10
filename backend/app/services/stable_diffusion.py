"""
Local Stable Diffusion image generation service (text -> image bytes).

Uses Hugging Face diffusers to avoid paid API image calls. Intended to feed
TripoSR with a locally generated reference image. Falls back to disabled state
when dependencies or models are unavailable.

IMPROVEMENTS:
- Eager loading at startup to detect issues early
- Timeout mechanism to prevent infinite hangs
- Retry logic for flaky model loading
"""
from __future__ import annotations

import logging
import gc
import os
import threading
import time
from io import BytesIO
from typing import Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

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


class ModelLoadingError(StableDiffusionError):
    """Error specifically during model loading."""


class StableDiffusionService:
    # Timeout for model loading (5 minutes should be enough)
    MODEL_LOAD_TIMEOUT_SECONDS = 300
    # Max retries for loading
    MAX_LOAD_RETRIES = 2
    
    def __init__(self) -> None:
        self.settings = get_settings()
        self.enabled = bool(self.settings.enable_stable_diffusion)
        self.model_id = self.settings.stable_diffusion_model
        self.height = self.settings.stable_diffusion_height
        self.width = self.settings.stable_diffusion_width
        self.num_steps = self.settings.stable_diffusion_steps
        self.guidance = self.settings.stable_diffusion_guidance
        self._pipe: Any = None
        self._loading = False
        self._load_error: Optional[str] = None
        self._load_lock = threading.Lock()
        
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

    def is_loaded(self) -> bool:
        """Check if the model is already loaded."""
        return self._pipe is not None
    
    def is_loading(self) -> bool:
        """Check if the model is currently loading."""
        return self._loading
    
    def get_load_error(self) -> Optional[str]:
        """Get the last loading error if any."""
        return self._load_error

    def _load_pipeline_internal(self) -> Any:
        """Internal method to load the pipeline. Called within a thread."""
        if _StableDiffusionPipeline is None:
            raise ModelLoadingError("Stable Diffusion dependencies not installed")
        
        logger.info("Loading Stable Diffusion model (this may take a few minutes on first run)...")
        
        # Set environment variable to help with potential hangs
        os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
        
        # Load model with local_files_only=True first to check cache
        pipe = None
        try:
            # First try loading from cache only (fast check)
            logger.info("Checking local cache...")
            pipe = _StableDiffusionPipeline.from_pretrained(
                self.model_id,
                torch_dtype=self._torch_dtype,
                safety_checker=None,
                requires_safety_checker=False,
                local_files_only=True,
            )
            logger.info("Model loaded from cache successfully")
        except Exception as cache_err:
            logger.info(f"Model not in cache or cache incomplete, downloading... ({cache_err})")
            # Download/load from HuggingFace
            pipe = _StableDiffusionPipeline.from_pretrained(
                self.model_id,
                torch_dtype=self._torch_dtype,
                safety_checker=None,
                requires_safety_checker=False,
                local_files_only=False,
            )
            logger.info("Model downloaded and loaded successfully")
        
        return pipe
    
    def _apply_optimizations(self, pipe: Any) -> None:
        """Apply memory optimizations to the pipeline."""
        logger.info("Applying memory optimizations...")
        
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

    def _ensure_pipeline(self, timeout: Optional[int] = None) -> None:
        """Ensure the pipeline is loaded, with timeout protection."""
        if self._pipe is not None:
            return
            
        if self._load_error:
            raise ModelLoadingError(f"Model previously failed to load: {self._load_error}")
        
        if not _SD_AVAILABLE or _StableDiffusionPipeline is None:
            raise StableDiffusionError("Stable Diffusion dependencies not installed")
        
        # Use lock to prevent multiple simultaneous loading attempts
        with self._load_lock:
            # Double-check after acquiring lock
            if self._pipe is not None:
                return
            
            self._loading = True
            timeout = timeout or self.MODEL_LOAD_TIMEOUT_SECONDS
            
            for attempt in range(self.MAX_LOAD_RETRIES + 1):
                try:
                    logger.info(f"Loading attempt {attempt + 1}/{self.MAX_LOAD_RETRIES + 1}")
                    
                    # Use ThreadPoolExecutor for timeout support
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(self._load_pipeline_internal)
                        try:
                            pipe = future.result(timeout=timeout)
                        except FuturesTimeoutError:
                            logger.error(f"Model loading timed out after {timeout} seconds")
                            self._load_error = f"Loading timed out after {timeout}s. Try restarting the backend."
                            raise ModelLoadingError(self._load_error)
                    
                    # Apply optimizations
                    self._apply_optimizations(pipe)
                    
                    # Move to device
                    logger.info(f"Moving model to device: {self.device}")
                    pipe.to(self.device)
                    self._pipe = pipe
                    self._load_error = None
                    logger.info("Stable Diffusion model loaded successfully!")
                    return
                    
                except ModelLoadingError:
                    # Don't retry timeout errors
                    raise
                except Exception as exc:
                    logger.error(f"Loading attempt {attempt + 1} failed: {exc}")
                    if attempt < self.MAX_LOAD_RETRIES:
                        logger.info("Retrying in 3 seconds...")
                        time.sleep(3)
                        # Clear any partial state
                        gc.collect()
                        if _torch is not None:
                            try:
                                _torch.cuda.empty_cache()
                            except Exception:
                                pass
                    else:
                        self._load_error = str(exc)
                        raise ModelLoadingError(f"Failed to load Stable Diffusion after {self.MAX_LOAD_RETRIES + 1} attempts: {exc}")
                finally:
                    self._loading = False

    def preload(self, timeout: Optional[int] = None) -> bool:
        """
        Eagerly load the model. Call this at startup to detect issues early.
        Returns True if loaded successfully, False otherwise.
        """
        if not self.enabled:
            logger.info("Stable Diffusion is disabled, skipping preload")
            return False
        
        try:
            self._ensure_pipeline(timeout=timeout)
            return True
        except Exception as e:
            logger.error(f"Preload failed: {e}")
            return False

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
            self._load_error = None

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


def preload_stable_diffusion(timeout: int = 300) -> bool:
    """
    Helper function to preload SD at startup.
    Call this from main.py lifespan or startup event.
    """
    try:
        service = get_stable_diffusion_service()
        return service.preload(timeout=timeout)
    except Exception as e:
        logger.error(f"SD preload helper failed: {e}")
        return False
