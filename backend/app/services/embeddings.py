"""
OpenAI embeddings service for generating text embeddings.

This module provides functions to generate embeddings using OpenAI's
embedding models. The client is created lazily to avoid network calls
during import.

Usage:
    from app.services.embeddings import embed_text, batch_embed

    # Single text embedding
    embedding = await embed_text("What is a humanoid robot?")

    # Batch embedding (more efficient for multiple texts)
    embeddings = await batch_embed(["Text 1", "Text 2", "Text 3"])
"""

from typing import Sequence
from openai import AsyncOpenAI, OpenAIError

from app.core.config import settings


# Global client instance (lazily initialized)
_client: AsyncOpenAI | None = None


def get_openai_client() -> AsyncOpenAI:
    """
    Get or create the OpenAI async client.

    The client is created once and reused for all embedding operations.
    Uses the API key from settings.

    Returns:
        AsyncOpenAI client instance

    Raises:
        ValueError: If OPENAI_API_KEY is not configured
    """
    global _client
    if _client is None:
        if not settings.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is not configured. "
                "Please set it in your environment variables or .env file."
            )
        _client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


async def embed_text(text: str) -> list[float]:
    """
    Generate embedding for a single text using OpenAI's embedding model.

    Args:
        text: Text to embed (will be truncated if too long)

    Returns:
        List of floats representing the embedding vector (1536 dimensions for text-embedding-3-small)

    Raises:
        ValueError: If text is empty or API key is not configured
        OpenAIError: If the API request fails

    Example:
        embedding = await embed_text("What is a humanoid robot?")
        print(f"Embedding dimension: {len(embedding)}")  # 1536
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    client = get_openai_client()

    try:
        response = await client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=text,
        )
        return response.data[0].embedding
    except OpenAIError as e:
        # Re-raise with more context
        raise OpenAIError(
            f"Failed to generate embedding: {str(e)}"
        ) from e


async def batch_embed(texts: Sequence[str], batch_size: int = 100) -> list[list[float]]:
    """
    Generate embeddings for multiple texts in batches.

    This is more efficient than calling embed_text() multiple times
    as it batches requests to the OpenAI API.

    Args:
        texts: List of texts to embed
        batch_size: Maximum number of texts per API call (default: 100, OpenAI's limit)

    Returns:
        List of embedding vectors, one for each input text

    Raises:
        ValueError: If texts list is empty or any text is empty
        OpenAIError: If any API request fails

    Example:
        texts = ["Text 1", "Text 2", "Text 3"]
        embeddings = await batch_embed(texts)
        print(f"Generated {len(embeddings)} embeddings")
    """
    if not texts:
        raise ValueError("Texts list cannot be empty")

    # Validate all texts are non-empty
    for i, text in enumerate(texts):
        if not text or not text.strip():
            raise ValueError(f"Text at index {i} is empty")

    client = get_openai_client()
    all_embeddings: list[list[float]] = []

    # Process in batches
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]

        try:
            response = await client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=list(batch),  # Convert to list for API
            )

            # Extract embeddings in order
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)

        except OpenAIError as e:
            # Re-raise with batch context
            raise OpenAIError(
                f"Failed to generate embeddings for batch {i // batch_size + 1}: {str(e)}"
            ) from e

    return all_embeddings


async def embed_query(query: str) -> list[float]:
    """
    Generate embedding for a search query.

    This is an alias for embed_text() with a more semantic name for
    query embedding use cases.

    Args:
        query: Search query text

    Returns:
        List of floats representing the query embedding vector

    Example:
        query_embedding = await embed_query("How do humanoid robots walk?")
    """
    return await embed_text(query)
