"""
Configuration management using Pydantic BaseSettings.

All configuration values are loaded from environment variables.
See backend/.env.example for required variables.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Environment variables are loaded from:
    1. System environment
    2. .env file (if present)

    All settings have sensible defaults where possible.
    Required settings (like API keys) will raise an error if missing.
    """

    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"

    # Qdrant Cloud Configuration
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION_NAME: str = "textbook_embeddings"

    # Neon Postgres Configuration
    DATABASE_URL: str

    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:3000,https://psqasim.github.io"

    # Application Limits
    MAX_QUESTION_TOKENS: int = 500
    MAX_SELECTION_TOKENS: int = 500
    CHUNK_RETRIEVAL_LIMIT: int = 10

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra environment variables
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """
        Parse CORS_ORIGINS from comma-separated string to list.

        Example:
            CORS_ORIGINS="http://localhost:3000,https://example.com"
            -> ["http://localhost:3000", "https://example.com"]

        Returns:
            List of allowed CORS origins with whitespace stripped
        """
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


@lru_cache
def get_settings() -> Settings:
    """
    Get cached Settings instance.

    Uses functools.lru_cache to ensure Settings is only instantiated once,
    avoiding repeated environment variable parsing.

    Returns:
        Cached Settings instance

    Example:
        from app.core.config import get_settings

        settings = get_settings()
        print(settings.OPENAI_API_KEY)
    """
    return Settings()


# Convenience: Pre-instantiated settings for direct import
settings = get_settings()
