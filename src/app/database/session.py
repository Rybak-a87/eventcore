import datetime
from typing import AsyncGenerator, Type, Any, Dict

from sqlalchemy import func, select

from sqlalchemy.orm import  DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.settings import settings
from app.database.mixins import CRUDMixin


class Base(DeclarativeBase, CRUDMixin):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), nullable=False, onupdate=func.now()
    )


engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True
)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
