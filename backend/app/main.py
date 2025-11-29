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

    yield

    logger.info("application_shutdown")


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

# Phase 3.4: Security middleware
app.add_middleware(SecurityHeadersMiddleware)  # Security headers
app.add_middleware(RateLimitMiddleware, requests_per_minute=60, requests_per_hour=1000)  # Rate limiting
app.add_middleware(FileSizeLimitMiddleware, max_size=50 * 1024 * 1024)  # 50MB file size limit

# Phase 3.2: Request tracing middleware
app.add_middleware(RequestTracingMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Mount static files for Phase 6.6 frontend demo
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")


@app.get("/", tags=["frontend"])
async def root():
    """Serve the main frontend UI"""
    from fastapi.responses import FileResponse
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path, media_type="text/html")
    return {"message": "CADLift API", "docs": "/docs"}


@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
    }
