"""
Health check endpoint for monitoring backend status.

This module provides a simple health check endpoint that returns
the operational status of the backend API. In Phase 3, it returns
a hardcoded "ok" status. Future phases will add checks for Qdrant
and Postgres connectivity.
"""

from fastapi import APIRouter

from app.core.config import settings


router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns basic health status and non-sensitive configuration info.
    In Phase 3, this returns a hardcoded "ok" status.
    Future phases will add:
    - Qdrant connectivity check (Phase 5)
    - Postgres connectivity check (Phase 4)

    Returns:
        dict: Health status information including:
            - status: "ok" if service is healthy
            - environment: Basic config info (no secrets)
    """
    return {
        "status": "ok",
        "environment": {
            "openai_chat_model": settings.OPENAI_CHAT_MODEL,
            "openai_embedding_model": settings.OPENAI_EMBEDDING_MODEL,
            "qdrant_collection": settings.QDRANT_COLLECTION_NAME,
            "max_question_tokens": settings.MAX_QUESTION_TOKENS,
            "max_selection_tokens": settings.MAX_SELECTION_TOKENS,
            "log_level": settings.LOG_LEVEL,
        },
    }
