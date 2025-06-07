import asyncio
from typing import Annotated, AsyncGenerator

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings


engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_size=50,
    max_overflow=50,
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a new SQLAlchemy async session."""
    async_session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
        )
    async with async_session() as session:
        yield session
