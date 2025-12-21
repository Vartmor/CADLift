from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.core.middleware import RequestTracingMiddleware
from app.core.security import (
    FileSizeLimitMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)
from app.db.base import Base
from app.db.session import engine

settings = get_settings()


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Configure structured logging with JSON output
    configure_logging(
        json_logs=not settings.debug,  # JSON in production, console in dev
        log_level=settings.log_level,
    )
    logger.info("application_startup", app_name=settings.app_name, environment=settings.environment)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Eager preload Stable Diffusion in background thread (non-blocking)
    # This helps detect issues early and warms up the model cache
    import threading
    def _preload_sd():
        try:
            from app.services.stable_diffusion import preload_stable_diffusion
            logger.info("Starting Stable Diffusion model preload in background...")
            success = preload_stable_diffusion(timeout=300)
            if success:
                logger.info("Stable Diffusion model preloaded successfully!")
            else:
                logger.warning("Stable Diffusion preload failed or disabled - will retry on first use")
        except Exception as e:
            logger.error(f"SD preload thread error: {e}")
    
    if settings.enable_stable_diffusion:
        preload_thread = threading.Thread(target=_preload_sd, daemon=True)
        preload_thread.start()
    else:
        logger.info("Stable Diffusion disabled, skipping preload")

    yield

    logger.info("application_shutdown")


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

# Phase 3.4: Security middleware
app.add_middleware(SecurityHeadersMiddleware)  # Security headers
app.add_middleware(RateLimitMiddleware)  # Rate limiting - uses high defaults for dev
app.add_middleware(FileSizeLimitMiddleware, max_size=50 * 1024 * 1024)  # 50MB file size limit

# Phase 3.2: Request tracing middleware
app.add_middleware(RequestTracingMiddleware)

# CORS middleware - uses environment-based configuration for security
# In production, set CORS_ORIGINS environment variable to specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_methods_list,
    allow_headers=settings.cors_headers_list,
    expose_headers=settings.cors_expose_headers_list,  # Allow frontend to read Content-Disposition
)

app.include_router(api_router)

# Mount static files for Phase 6.6 frontend demo
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")


@app.get("/", tags=["info"])
async def root():
    """API landing page with links to docs"""
    from fastapi.responses import FileResponse
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path, media_type="text/html")
    # Fallback to JSON if HTML not found
    return {
        "name": "CADLift API",
        "version": "1.0.0",
        "description": "Open-source 3D generation platform",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
    }
