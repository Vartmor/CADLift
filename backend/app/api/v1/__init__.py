from fastapi import APIRouter

from .auth import router as auth_router
from .files import router as files_router
from .jobs import router as jobs_router

router_v1 = APIRouter(prefix="/api/v1")
router_v1.include_router(auth_router)
router_v1.include_router(jobs_router)
router_v1.include_router(files_router)
