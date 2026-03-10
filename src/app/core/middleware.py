from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.settings import settings


def setup_cors(app: FastAPI) -> None:
    # `settings.cors_origins` is typed as `list[AnyHttpUrl]` (Pydantic v2 returns Url objects),
    # while Starlette's `CORSMiddleware` expects plain strings and compares them to the incoming
    # `Origin` header. Normalize to strings to avoid silent mismatches like:
    # Origin: "http://localhost:5173" vs allow_origins: [Url("http://localhost:5173/")].
    allow_origins = [str(origin).rstrip("/") for origin in settings.cors_origins if str(origin)]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
