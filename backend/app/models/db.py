"""
SQLAlchemy models for chat session persistence in Neon Postgres.

Models:
- ChatSession: Represents a chat conversation session
- ChatMessage: Individual messages within a session

Design decisions:
- UUID primary keys for distributed system compatibility
- Timestamps on all records for audit trail
- Nullable user_id to support anonymous users
- Enum types for mode and role to ensure data consistency
"""

import uuid
from datetime import datetime, UTC
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class ChatSession(Base):
    """
    Chat session model for tracking conversation context.

    A session represents a single conversation, which can contain
    multiple messages. Sessions track the mode (whole-book vs selection)
    and user identity (if authenticated).

    Attributes:
        id: Unique session identifier (UUID)
        user_id: User identifier (nullable for anonymous users)
        mode: Chat mode - "whole-book" or "selection"
        started_at: When the session was created
        ended_at: When the session was closed (nullable, for future use)
        created_at: Record creation timestamp
        updated_at: Record last update timestamp
        messages: Relationship to ChatMessage records
    """

    __tablename__ = "chat_sessions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    user_id = Column(
        String,
        nullable=True,
        index=True,
        comment="User identifier - nullable for anonymous users",
    )
    mode = Column(
        SQLEnum("whole-book", "selection", name="chat_mode"),
        nullable=False,
        comment="Chat mode: whole-book or selection-based",
    )
    started_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        comment="Session start timestamp",
    )
    ended_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Session end timestamp (future use)",
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
        comment="Record creation timestamp",
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
        comment="Record last update timestamp",
    )

    # Relationship to messages (one-to-many)
    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",  # Eagerly load messages with session
    )

    def __repr__(self) -> str:
        return (
            f"<ChatSession(id={self.id}, user_id={self.user_id}, "
            f"mode={self.mode}, started_at={self.started_at})>"
        )


class ChatMessage(Base):
    """
    Chat message model for individual user and assistant messages.

    Each message belongs to a session and contains the message content,
    role (user or assistant), and optional context for selection-based queries.

    Attributes:
        id: Unique message identifier (UUID)
        session_id: Foreign key to ChatSession
        role: Message role - "user" or "assistant"
        content: Message text content
        selected_text: User-selected text (selection mode only)
        doc_path: Document path for selection context
        created_at: When the message was created
        session: Relationship to ChatSession
    """

    __tablename__ = "chat_messages"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to chat_sessions",
    )
    role = Column(
        SQLEnum("user", "assistant", name="message_role"),
        nullable=False,
        comment="Message role: user or assistant",
    )
    content = Column(
        Text,
        nullable=False,
        comment="Message text content",
    )
    selected_text = Column(
        Text,
        nullable=True,
        comment="User-selected text for selection-based queries",
    )
    doc_path = Column(
        String,
        nullable=True,
        comment="Document path for selection context",
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
        comment="Message creation timestamp",
    )

    # Relationship to session (many-to-one)
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self) -> str:
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return (
            f"<ChatMessage(id={self.id}, session_id={self.session_id}, "
            f"role={self.role}, content='{content_preview}')>"
        )
