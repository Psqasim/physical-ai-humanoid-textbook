"""
Dependency injection helpers for FastAPI.

This module provides dependency functions that can be used with FastAPI's
Depends() to inject services, clients, and configuration into route handlers.

Example:
    from fastapi import Depends
    from app.core.deps import get_settings

    @app.get("/config")
    def read_config(settings: Settings = Depends(get_settings)):
        return {"model": settings.OPENAI_CHAT_MODEL}
"""

from typing import Annotated, AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from qdrant_client import AsyncQdrantClient
from openai import AsyncOpenAI

from app.core.config import Settings, get_settings as _get_settings
from app.db.session import get_db as _get_db
from app.services.qdrant import get_qdrant_client as _get_qdrant_client
from app.services.embeddings import get_openai_client as _get_openai_client


def get_settings() -> Settings:
    """
    Dependency to inject Settings into route handlers.

    Returns:
        Cached Settings instance

    Example:
        from fastapi import Depends
        from app.core.deps import get_settings

        @router.get("/info")
        def get_info(settings: Settings = Depends(get_settings)):
            return {"embedding_model": settings.OPENAI_EMBEDDING_MODEL}
    """
    return _get_settings()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to inject database session (AsyncSession).

    Implemented in Phase 4 (Neon Postgres Models & Session Management).

    Yields:
        AsyncSession: Database session that is automatically closed after request

    Example:
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.core.deps import get_db

        @router.get("/sessions")
        async def list_sessions(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(ChatSession))
            return result.scalars().all()
    """
    async for session in _get_db():
        yield session


def get_qdrant_client() -> AsyncQdrantClient:
    """
    Dependency to inject Qdrant client.

    Implemented in Phase 5 (Qdrant Client Configuration).

    Returns:
        AsyncQdrantClient: Configured Qdrant async client

    Example:
        from qdrant_client import AsyncQdrantClient
        from app.core.deps import get_qdrant_client

        @router.get("/collections")
        async def list_collections(client: AsyncQdrantClient = Depends(get_qdrant_client)):
            collections = await client.get_collections()
            return collections
    """
    return _get_qdrant_client()


def get_openai_client() -> AsyncOpenAI:
    """
    Dependency to inject OpenAI client.

    Implemented in Phase 5/6 (Embeddings Service).

    Returns:
        AsyncOpenAI: Configured OpenAI async client

    Example:
        from openai import AsyncOpenAI
        from app.core.deps import get_openai_client

        @router.post("/embed")
        async def create_embedding(
            text: str,
            client: AsyncOpenAI = Depends(get_openai_client)
        ):
            response = await client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
    """
    return _get_openai_client()


# Annotated type aliases for cleaner dependency injection
SettingsDep = Annotated[Settings, Depends(get_settings)]
DBSessionDep = Annotated[AsyncSession, Depends(get_db)]
QdrantClientDep = Annotated[AsyncQdrantClient, Depends(get_qdrant_client)]
OpenAIClientDep = Annotated[AsyncOpenAI, Depends(get_openai_client)]


# Export all dependencies
__all__ = [
    "get_settings",
    "get_db",
    "get_qdrant_client",
    "get_openai_client",
    "SettingsDep",
    "DBSessionDep",
    "QdrantClientDep",
    "OpenAIClientDep",
]
