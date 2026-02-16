# import redis.asyncio as redis

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.admin_panel import get_admin
from app.api.routers import routers
from app.core.settings import settings

# from contextlib import asynccontextmanager
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     from app.database.session import engine
#     if settings.database_url.startswith("sqlite+aiosqlite:///"):
#         path = settings.database_url.split("///./")[-1]
#         import os
#         if not os.path.isfile(path):
#
#             async with engine.begin() as conn:
#                 from app.database.session import Base
#                 await conn.run_sync(Base.metadata.create_all)
#                 print("--- Create tables ---")
#
#     yield  # <--- the application works here
#
#     # code that runs when the application stops
#     # For example, engine.dispose()
#     await engine.dispose()




tags_metadata = [
    # {
    #     "name": "name_tags_metadata",
    #     "description": "description_tags_metadata"
    # },
    # {
    #     "name": "name_tags_metadata2",
    #     "description": "description_tags_metadata2"
    # },
]


app = FastAPI(
    title="EventCore API",
    description="In development",
    version="0.0.0",
    openapi_tags=tags_metadata,
    docs_url=None if settings.is_production else "/swagger",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
    debug=not settings.is_production,
    # lifespan=lifespan,
)

app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")
app.include_router(router=routers)

get_admin(app)

if not settings.is_production:
    @app.get("/")
    def welcome():
        return {
            "swagger_url": f"http://{settings.server_host}:{settings.server_port}/swagger",
            "redoc_url": f"http://{settings.server_host}:{settings.server_port}/redoc",
            "openapi_url": f"http://{settings.server_host}:{settings.server_port}/openapi.json",
        }


    @app.get("/check-health-db")
    async def health():
        try:
            from app.database.session import engine
            async with engine.connect() as conn:
                from sqlalchemy import text
                await conn.execute(text("SELECT 1"))
            status_db = "ok"
        except Exception as e:
            status_db = f"error: {e}"
        return {"status": "ok", "database": status_db}
