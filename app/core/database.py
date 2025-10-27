"""Database utilities with SQLAlchemy async support."""

import logging
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.config import settings

logger = logging.getLogger(__name__)

# Database engine and session factory
engine = None
async_session_maker = None


class Base(DeclarativeBase):
    """Base class for database models."""

    pass


def init_database():
    """Initialize database connection."""
    global engine, async_session_maker

    if not settings.database_url:
        logger.warning("No database URL provided, running without database")
        return

    # Convert postgres:// to postgresql+asyncpg:// for async support
    database_url = settings.database_url
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://")

    engine = create_async_engine(
        database_url,
        echo=settings.debug,
        poolclass=NullPool if settings.environment == "test" else None,
        pool_pre_ping=True,
    )
    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    logger.info("Database connection initialized")


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    if not async_session_maker:
        logger.warning("Database not initialized")
        return

    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_database_sync() -> Optional[AsyncSession]:
    """Get database session (for dependency injection)."""
    if not async_session_maker:
        return None
    return async_session_maker()


async def check_database_health() -> bool:
    """Check database health."""
    if not engine:
        return False

    try:
        async with engine.begin() as conn:
            from sqlalchemy import text
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def close_database():
    """Close database connections."""
    global engine
    if engine:
        await engine.dispose()
        logger.info("Database connections closed")

