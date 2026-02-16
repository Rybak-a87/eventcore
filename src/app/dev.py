from app.database.models import *

def run_db(delete: bool = False) -> None:
    import asyncio
    async def create_delete_db() -> None:
        from app.database.session import engine, Base
        async with engine.begin() as conn:
            if delete:
                await conn.run_sync(Base.metadata.drop_all)
                print("--- Delete tables ---")
            else:
                await conn.run_sync(Base.metadata.create_all)
                print("--- Create tables ---")
            print(f"--- {Base.metadata.tables.keys()} ---")
    asyncio.run(create_delete_db())


def run_app() -> None:
    import uvicorn
    from app.core.settings import settings
    uvicorn.run(
        app="app.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=True,
    )


# if __name__ == '__main__':
#     run_app()
