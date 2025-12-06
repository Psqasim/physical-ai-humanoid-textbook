"""
Pydantic schemas for API request/response validation.

These schemas define the structure of data exchanged between the
frontend and backend API. They provide automatic validation and
documentation for FastAPI endpoints.

Models:
- ChatRequest: Incoming chat question with mode and context
- Citation: Source reference for RAG-generated answers
- ChatResponse: Outgoing answer with citations
- HealthResponse: Health check endpoint response
"""

from typing import Literal
from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """
    Request schema for POST /api/chat endpoint.

    Supports two modes:
    1. whole-book: Query the entire textbook
    2. selection: Query based on user-selected text

    Attributes:
        mode: Chat mode ("whole-book" or "selection")
        question: User's question (max 500 tokens, validated by backend)
        selectedText: Text selected by user (required for selection mode)
        docPath: Document path for selection context (required for selection mode)
        userId: Optional user identifier for session persistence
    """

    mode: Literal["whole-book", "selection"] = Field(
        ...,
        description="Chat mode: whole-book for general queries, selection for context-specific queries",
    )
    question: str = Field(
        ...,
        min_length=1,
        max_length=5000,  # Character limit (tokens validated separately by backend)
        description="User's question",
        examples=["What are the main applications of humanoid robots?"],
    )
    selectedText: str | None = Field(
        None,
        max_length=10000,
        description="Text selected by user (required for selection mode)",
    )
    docPath: str | None = Field(
        None,
        max_length=500,
        description="Document path for selection context (e.g., 'docs/01-introduction.md')",
        examples=["docs/01-introduction.md", "docs/chapters/02-fundamentals.mdx"],
    )
    userId: str | None = Field(
        None,
        max_length=255,
        description="User identifier for session persistence (optional, nullable for anonymous users)",
    )

    @field_validator("selectedText", "docPath")
    @classmethod
    def validate_selection_mode(cls, v, info):
        """
        Validate that selectedText and docPath are provided for selection mode.

        This validation happens in the backend. For now, we allow None values
        and will enforce the constraint in the endpoint handler.
        """
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "mode": "whole-book",
                    "question": "What are the main components of a humanoid robot?",
                    "userId": "user123",
                },
                {
                    "mode": "selection",
                    "question": "Can you explain this concept in more detail?",
                    "selectedText": "Bipedal locomotion requires sophisticated control systems...",
                    "docPath": "docs/03-locomotion.md",
                    "userId": "user123",
                },
            ]
        }
    }


class Citation(BaseModel):
    """
    Source citation for RAG-generated answers.

    Each citation links to a specific section of the textbook
    that was used to generate the answer.

    Attributes:
        docPath: Relative path to the source document
        heading: Section heading from the document
        snippet: Text excerpt from the source (50-100 words)
    """

    docPath: str = Field(
        ...,
        description="Relative path to source document",
        examples=["docs/01-introduction.md", "docs/chapters/02-fundamentals.mdx"],
    )
    heading: str = Field(
        ...,
        description="Section heading from the document",
        examples=["Introduction to Humanoid Robots", "Chapter 2: Fundamentals"],
    )
    snippet: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Text excerpt from the source (50-100 words)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "docPath": "docs/01-introduction.md",
                    "heading": "Applications of Humanoid Robots",
                    "snippet": "Humanoid robots are designed to perform tasks in human-centric environments...",
                }
            ]
        }
    }


class ChatResponse(BaseModel):
    """
    Response schema for POST /api/chat endpoint.

    Returns the AI-generated answer along with source citations
    and the mode that was used.

    Attributes:
        answer: AI-generated answer to the user's question
        citations: List of source references (3-5 citations)
        mode: Chat mode used ("whole-book" or "selection")
    """

    answer: str = Field(
        ...,
        min_length=1,
        description="AI-generated answer to the user's question",
    )
    citations: list[Citation] = Field(
        default_factory=list,
        description="List of source references (typically 3-5 citations)",
    )
    mode: Literal["whole-book", "selection"] = Field(
        ...,
        description="Chat mode that was used for this response",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "answer": "Humanoid robots have several main components including sensors, actuators, control systems, and power sources...",
                    "citations": [
                        {
                            "docPath": "docs/02-components.md",
                            "heading": "Robot Components Overview",
                            "snippet": "The main components of a humanoid robot include...",
                        }
                    ],
                    "mode": "whole-book",
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """
    Response schema for GET /api/health endpoint.

    Returns the operational status of the backend and its dependencies.

    Attributes:
        status: Overall health status ("ok", "degraded", or "error")
        environment: Non-sensitive configuration information
        database: Database connectivity status (future enhancement)
        qdrant: Qdrant connectivity status (future enhancement)
    """

    status: Literal["ok", "degraded", "error"] = Field(
        ...,
        description="Overall health status",
    )
    environment: dict[str, str | int] = Field(
        default_factory=dict,
        description="Non-sensitive configuration information",
    )
    database: dict[str, str] | None = Field(
        None,
        description="Database connectivity status (future enhancement)",
    )
    qdrant: dict[str, str] | None = Field(
        None,
        description="Qdrant connectivity status (future enhancement)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "ok",
                    "environment": {
                        "openai_chat_model": "gpt-4o-mini",
                        "qdrant_collection": "textbook_embeddings",
                    },
                    "database": {"status": "connected"},
                    "qdrant": {"status": "connected", "collections": 1},
                }
            ]
        }
    }
