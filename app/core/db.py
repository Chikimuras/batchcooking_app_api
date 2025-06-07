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
    
    This function provides an async context-managed session using SQLAlchemy's async sessionmaker, ensuring proper session lifecycle management for each use.
    	
    Yields:
        An AsyncSession instance for performing asynchronous database operations.
    """
    async_session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
        )
    async with async_session() as session:
        yield session
