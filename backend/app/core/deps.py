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

from app.core.config import Settings, get_settings as _get_settings
from app.db.session import get_db as _get_db


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


def get_qdrant_client():
    """
    Dependency to inject Qdrant client.

    Will be implemented in Phase 5 (Qdrant Client Configuration).

    Returns:
        QdrantClient: Configured Qdrant client

    Example:
        from qdrant_client import QdrantClient
        from app.core.deps import get_qdrant_client

        @router.get("/collections")
        def list_collections(client: QdrantClient = Depends(get_qdrant_client)):
            return client.get_collections()
    """
    raise NotImplementedError(
        "get_qdrant_client dependency not yet implemented. "
        "Will be added in Phase 5 (Qdrant Client Configuration)."
    )


def get_openai_client():
    """
    Dependency to inject OpenAI client.

    Will be implemented in Phase 6 (Indexing Pipeline) or Phase 7 (RAG).

    Returns:
        OpenAI: Configured OpenAI client

    Example:
        from openai import OpenAI
        from app.core.deps import get_openai_client

        @router.post("/embed")
        def create_embedding(
            text: str,
            client: OpenAI = Depends(get_openai_client)
        ):
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
    """
    raise NotImplementedError(
        "get_openai_client dependency not yet implemented. "
        "Will be added in Phase 6 (Indexing Pipeline)."
    )


# Annotated type aliases for cleaner dependency injection
SettingsDep = Annotated[Settings, Depends(get_settings)]
DBSessionDep = Annotated[AsyncSession, Depends(get_db)]


# Export all dependencies
__all__ = [
    "get_settings",
    "get_db",
    "get_qdrant_client",
    "get_openai_client",
    "SettingsDep",
    "DBSessionDep",
]
