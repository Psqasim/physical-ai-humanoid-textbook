"""
Chat session and message persistence service.

This module handles storing chat sessions and messages in Neon Postgres.

Key rules (from spec):
- ONLY persist when userId is provided (non-null, non-empty)
- Anonymous users (no userId) are NOT tracked
- Each chat request creates a new session
- Sessions store both user questions and assistant answers
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import get_logger
from app.models.db import ChatSession, ChatMessage
from app.models.schemas import ChatRequest, ChatResponse

logger = get_logger(__name__)


def should_persist(user_id: str | None) -> bool:
    """
    Check if chat should be persisted based on user_id.

    Per spec FR-021: Only persist when userId is provided (non-null, non-empty).
    Anonymous users are not tracked.

    Args:
        user_id: User identifier from request

    Returns:
        True if chat should be persisted, False otherwise
    """
    return user_id is not None and user_id.strip() != ""


async def create_session(
    user_id: str,
    mode: str,
    db: AsyncSession,
) -> ChatSession:
    """
    Create a new chat session.

    Args:
        user_id: User identifier
        mode: Chat mode ("whole-book" or "selection")
        db: Database session

    Returns:
        Created ChatSession object
    """
    session = ChatSession(
        user_id=user_id,
        mode=mode,
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    logger.info(f"Created chat session: id={session.id}, user_id={user_id}, mode={mode}")
    return session


async def add_user_message(
    session: ChatSession,
    request: ChatRequest,
    db: AsyncSession,
) -> ChatMessage:
    """
    Add user message to session.

    Args:
        session: Chat session to add message to
        request: Chat request with user's question and context
        db: Database session

    Returns:
        Created ChatMessage object
    """
    message = ChatMessage(
        session_id=session.id,
        role="user",
        content=request.question,
        selected_text=request.selectedText,
        doc_path=request.docPath,
    )

    db.add(message)
    await db.commit()
    await db.refresh(message)

    logger.debug(f"Added user message to session {session.id}")
    return message


async def add_assistant_message(
    session: ChatSession,
    response: ChatResponse,
    db: AsyncSession,
) -> ChatMessage:
    """
    Add assistant message to session.

    Args:
        session: Chat session to add message to
        response: Chat response with assistant's answer
        db: Database session

    Returns:
        Created ChatMessage object
    """
    message = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=response.answer,
        # Note: selected_text and doc_path are None for assistant messages
    )

    db.add(message)
    await db.commit()
    await db.refresh(message)

    logger.debug(f"Added assistant message to session {session.id}")
    return message


async def save_chat_interaction(
    request: ChatRequest,
    response: ChatResponse,
    db: AsyncSession,
) -> ChatSession | None:
    """
    Save entire chat interaction (session + user message + assistant message).

    This is the main entry point for persisting chat data.
    Only persists if userId is provided (non-null, non-empty).

    Args:
        request: Chat request from user
        response: Chat response from assistant
        db: Database session

    Returns:
        Created ChatSession if persisted, None if skipped (anonymous user)

    Raises:
        Exception: If database operations fail
    """
    # Check if we should persist
    if not should_persist(request.userId):
        logger.info("Skipping persistence for anonymous user")
        return None

    logger.info(f"Persisting chat interaction for user: {request.userId}")

    try:
        # Create session
        session = await create_session(
            user_id=request.userId,
            mode=request.mode,
            db=db,
        )

        # Add user message
        await add_user_message(session, request, db)

        # Add assistant message
        await add_assistant_message(session, response, db)

        logger.info(
            f"Successfully persisted chat interaction: session_id={session.id}"
        )
        return session

    except Exception as e:
        logger.error(f"Failed to persist chat interaction: {e}", exc_info=True)
        # Don't let storage failures crash the chat request
        # The user already got their answer, storage is secondary
        await db.rollback()
        raise
