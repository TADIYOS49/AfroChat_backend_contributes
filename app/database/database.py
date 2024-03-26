from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from app.utils.logger import SQLAlchemyLogger as logger
from config import initial_config as config

engine = create_async_engine(
    url=config.POSTGRES_URL,
    future=True,
    # echo=True,
    pool_size=config.DATABSE_POOL_SIZE,
    max_overflow=config.DATABSE_POOL_OVERFLOW,
    pool_recycle=config.DATABASE_POOL_RECYCLE,
)

AsyncSessionFactory: async_sessionmaker = async_sessionmaker(
    engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)


async def get_db() -> AsyncGenerator:
    async with AsyncSessionFactory() as session:
        logger.debug(f"ASYNC Pool: {engine.pool.status()}")
        yield session


@asynccontextmanager
async def get_db_context() -> AsyncGenerator:
    async with AsyncSessionFactory() as session:
        yield session
