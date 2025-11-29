from fastapi import APIRouter

from app.api.v1 import router_v1

api_router = APIRouter()
api_router.include_router(router_v1)
