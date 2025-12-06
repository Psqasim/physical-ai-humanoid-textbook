"""
Logging configuration for the application.

Sets up structured logging based on LOG_LEVEL from settings.
"""

import logging
import sys
from typing import Any

from app.core.config import get_settings


def setup_logging() -> logging.Logger:
    """
    Configure and return the application logger.

    Configures:
    - Log level from settings (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    - Format: timestamp, level, logger name, message
    - Output: stdout (captured by hosting platforms)

    Returns:
        Configured logger instance

    Example:
        from app.core.logging import setup_logging

        logger = setup_logging()
        logger.info("Application started")
        logger.error("An error occurred", exc_info=True)
    """
    settings = get_settings()

    # Get or create logger
    logger = logging.getLogger("rag_backend")

    # Convert string log level to logging constant
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Avoid duplicate handlers if setup_logging is called multiple times
    if logger.handlers:
        return logger

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Get a logger instance with optional name.

    Args:
        name: Logger name (typically __name__ from calling module).
              If None, returns the root application logger.

    Returns:
        Logger instance

    Example:
        from app.core.logging import get_logger

        logger = get_logger(__name__)
        logger.info("Processing request")
    """
    if name:
        return logging.getLogger(f"rag_backend.{name}")
    return logging.getLogger("rag_backend")


def log_config_on_startup() -> None:
    """
    Log configuration summary on application startup.

    Useful for debugging deployment issues.
    Logs non-sensitive configuration values.

    Example:
        from app.core.logging import log_config_on_startup

        @app.on_event("startup")
        async def startup():
            log_config_on_startup()
    """
    settings = get_settings()
    logger = get_logger(__name__)

    logger.info("=" * 60)
    logger.info("RAG Backend Configuration")
    logger.info("=" * 60)
    logger.info(f"Log Level: {settings.LOG_LEVEL}")
    logger.info(f"OpenAI Embedding Model: {settings.OPENAI_EMBEDDING_MODEL}")
    logger.info(f"OpenAI Chat Model: {settings.OPENAI_CHAT_MODEL}")
    logger.info(f"Qdrant Collection: {settings.QDRANT_COLLECTION_NAME}")
    logger.info(f"CORS Origins: {settings.cors_origins_list}")
    logger.info(f"Max Question Tokens: {settings.MAX_QUESTION_TOKENS}")
    logger.info(f"Max Selection Tokens: {settings.MAX_SELECTION_TOKENS}")
    logger.info(f"Chunk Retrieval Limit: {settings.CHUNK_RETRIEVAL_LIMIT}")
    logger.info("=" * 60)


# Pre-configured logger for convenience
logger = setup_logging()
