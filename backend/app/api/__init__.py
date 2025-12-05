from fastapi import APIRouter

from app.api.v1 import router_v1
from app.api.websocket import router as websocket_router

api_router = APIRouter()
api_router.include_router(router_v1)
api_router.include_router(websocket_router)
