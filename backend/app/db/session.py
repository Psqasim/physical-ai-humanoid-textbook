"""
Async SQLAlchemy session management for Neon Postgres.

This module provides:
- Async SQLAlchemy engine configuration
- AsyncSession factory for database operations
- get_db() dependency for FastAPI endpoints

The engine is lazily initialized to avoid connection attempts during
import time. Actual database connections are established when needed.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from app.core.config import settings


# Global engine instance (lazily initialized)
_engine: AsyncEngine | None = None


def get_engine() -> AsyncEngine:
    """
    Get or create the async SQLAlchemy engine.

    The engine is created once and reused for all database operations.
    Uses asyncpg driver for Neon Postgres compatibility.

    Configuration:
    - pool_pre_ping: Verify connections are alive before using
    - echo: Log SQL queries if LOG_LEVEL is DEBUG (future enhancement)

    Returns:
        AsyncEngine instance configured for Neon Postgres
    """
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,  # Set to True for SQL query logging in development
            pool_pre_ping=True,  # Verify connections before using
            pool_size=5,  # Connection pool size (adjust based on load)
            max_overflow=10,  # Max connections beyond pool_size
        )
    return _engine


# AsyncSession factory
# Uses get_engine() to ensure engine is initialized
AsyncSessionLocal = async_sessionmaker(
    bind=get_engine(),
    class_=AsyncSession,
    expire_on_commit=False,  # Keep objects usable after commit
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an async database session.

    Usage in endpoints:
        @router.post("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Model))
            return result.scalars().all()

    The session is automatically closed after the request completes,
    even if an exception occurs.

    Yields:
        AsyncSession for database operations

    Example:
        from fastapi import Depends
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.db.session import get_db

        async def create_session(db: AsyncSession = Depends(get_db)):
            session = ChatSession(user_id="user123", mode="whole-book")
            db.add(session)
            await db.commit()
            await db.refresh(session)
            return session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
