from fastapi import APIRouter

from app.api.routers.v1.auth import router as auth_router
from app.api.routers.v1.accounts import router as accounts_router
from app.api.routers.v1.events import router as events_router


routers_v1 = APIRouter(prefix="/v1")

routers_v1.include_router(auth_router)
routers_v1.include_router(accounts_router)
routers_v1.include_router(events_router)