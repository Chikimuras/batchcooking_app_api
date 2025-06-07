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
    """
    Yields an asynchronous SQLAlchemy session for database operations.
    
    This async generator provides a managed `AsyncSession` instance, ensuring proper resource handling for each use.
    """
    async_session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
        )
    async with async_session() as session:
        yield session
