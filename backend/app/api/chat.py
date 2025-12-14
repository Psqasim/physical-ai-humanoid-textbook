"""
Chat API endpoints for RAG-powered Study Assistant.

Endpoints:
- POST /api/chat: Main chat endpoint for whole-book and selection-based Q&A
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.config import settings
from app.core.logging import get_logger
from app.core.i18n import detect_language, get_fallback_language
from app.db.session import get_db
from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag import answer_chat_request
from app.services.chat_storage import save_chat_interaction

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a question about the textbook",
    description="""
    RAG-powered Q&A endpoint supporting two modes:

    1. **whole-book**: Query the entire textbook corpus
    2. **selection**: Query based on user-selected text (requires selectedText and docPath)

    The endpoint:
    - Retrieves relevant chunks from the textbook using vector search
    - Generates an answer using OpenAI's chat model
    - Returns citations to source material
    - Optionally persists the chat session (if userId is provided)
    """,
    responses={
        200: {
            "description": "Successful response with answer and citations",
            "content": {
                "application/json": {
                    "example": {
                        "answer": "ROS 2 (Robot Operating System 2) is a flexible framework for writing robot software...",
                        "citations": [
                            {
                                "docPath": "/docs/module-1-ros2/chapter-1",
                                "heading": "What is ROS 2?",
                                "snippet": "ROS 2 is the second generation of the Robot Operating System...",
                            }
                        ],
                        "mode": "whole-book",
                    }
                }
            },
        },
        400: {
            "description": "Invalid request (e.g., missing selectedText for selection mode)",
            "content": {
                "application/json": {
                    "example": {"detail": "mode='selection' requires both selectedText and docPath"}
                }
            },
        },
        500: {
            "description": "Internal server error (e.g., OpenAI API failure)",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to generate answer. Please try again later."}
                }
            },
        },
        503: {
            "description": "Service unavailable (e.g., Qdrant connection failure)",
            "content": {
                "application/json": {
                    "example": {"detail": "The chatbot service is temporarily unavailable."}
                }
            },
        },
    },
)
async def chat_endpoint(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """
    Process a chat request and return an AI-generated answer with citations.

    Args:
        request: Chat request with mode, question, and optional context
        db: Database session (injected by FastAPI)

    Returns:
        ChatResponse with answer, citations, and mode

    Raises:
        HTTPException: For validation errors or API failures
    """
    # Log incoming request (excluding PII)
    logger.info(
        f"POST /api/chat: mode={request.mode}, "
        f"question_len={len(request.question)}, "
        f"has_user_id={request.userId is not None}"
    )

    # Validate selection mode requirements
    if request.mode == "selection":
        if not request.selectedText or not request.selectedText.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="mode='selection' requires selectedText to be provided and non-empty",
            )
        if not request.docPath or not request.docPath.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="mode='selection' requires docPath to be provided and non-empty",
            )

    # Validate question length (basic check, token validation could be added)
    if len(request.question.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question is too short. Please provide a meaningful question.",
        )

    if len(request.question) > 5000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question is too long. Please keep it under 5000 characters.",
        )

    # Detect language from user's question
    timestamp = datetime.utcnow().isoformat()
    detection_result = detect_language(request.question)
    detected_lang = detection_result["detectedLanguage"]
    confidence = detection_result["confidence"]
    fallback_applied = detection_result["fallbackApplied"]

    # Determine response language using fallback logic if needed
    fallback_lang = get_fallback_language(confidence, request.preferredLanguage)
    response_lang = fallback_lang if fallback_lang else detected_lang

    # Log language analytics (no PII - no message content)
    logger.info(
        f"Chat language analytics - "
        f"timestamp: {timestamp}, "
        f"detected_input_language: {detected_lang}, "
        f"confidence: {confidence:.2f}, "
        f"requested_language: {request.preferredLanguage}, "
        f"response_language: {response_lang}, "
        f"fallback_applied: {fallback_applied or fallback_lang is not None}"
    )

    # Process chat request through RAG pipeline
    try:
        response = await answer_chat_request(
            request=request,
            db=db,
            settings_override=None,  # Use default settings
        )

    except ValueError as e:
        # Validation errors from RAG pipeline
        logger.warning(f"Validation error in RAG pipeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(f"Failed to process chat request: {e}", exc_info=True)

        # Check if it's a Qdrant/network error
        error_msg = str(e).lower()
        if "qdrant" in error_msg or "connection" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="The chatbot service is temporarily unavailable. Please try again later.",
            )

        # OpenAI API errors
        if "openai" in error_msg or "rate limit" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="The chatbot is temporarily overloaded. Please try again in a moment.",
            )

        # Generic error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate answer. Please try again later.",
        )

    # Persist chat interaction (if userId provided)
    # Note: Storage failures should NOT crash the request since user already has their answer
    try:
        await save_chat_interaction(request, response, db)
    except Exception as e:
        # Log but don't fail the request
        logger.error(
            f"Failed to persist chat interaction (user still got answer): {e}",
            exc_info=True,
        )

    # Add language metadata to response
    response.detectedInputLanguage = detected_lang
    response.responseLanguage = response_lang
    response.fallbackApplied = fallback_applied or (fallback_lang is not None)

    logger.info(
        f"Chat request completed successfully: "
        f"answer_len={len(response.answer)}, citations={len(response.citations)}, "
        f"language: {response_lang}"
    )

    return response
