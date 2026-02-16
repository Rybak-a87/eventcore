from fastapi import APIRouter

from app.api.routers.v1 import routers_v1


routers = APIRouter(prefix="/api")

routers.include_router(routers_v1)
