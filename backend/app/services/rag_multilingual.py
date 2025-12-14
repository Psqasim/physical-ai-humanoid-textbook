"""
RAG multilingual service for language-aware document indexing and retrieval.

This module extends the base RAG functionality with multilingual support:
- Language-tagged document indexing
- Language-filtered similarity search
- Fallback to English when target language content is unavailable

Usage:
    from app.services.rag_multilingual import (
        index_document,
        search_with_language_filter,
        MultilingualEmbeddingChunk,
    )

    # Index a document with language metadata
    await index_document(
        doc_text="ROS 2 روبوٹکس سسٹم کے لیے ایک فریم ورک ہے",
        doc_id="intro-ros2-ur",
        language="ur",
        original_language="en",
        translation_source="human"
    )

    # Search with language filter
    results = await search_with_language_filter(
        query="ROS 2 کیا ہے؟",
        language="ur",
        limit=5
    )
"""

import asyncio
from typing import Literal, Sequence
from dataclasses import dataclass
from uuid import uuid4

from qdrant_client.models import (
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    PayloadSchemaType,
)

from app.services.qdrant import get_qdrant_client, get_sync_qdrant_client
from app.services.embeddings import batch_embed
from app.core.config import settings


# Type aliases for language codes
LanguageCode = Literal["en", "ur", "ja"]
TranslationSource = Literal["original", "human", "machine"]
ContentType = Literal["ui", "docs", "chat_context"]


@dataclass
class MultilingualEmbeddingChunk:
    """
    Data model for a multilingual embedding chunk.

    This extends the base EmbeddingChunk with language metadata fields
    as defined in the data model specification (data-model.md).

    Attributes:
        id: Unique identifier (format: "doc_id:chunk_index")
        vector: Embedding vector (1536 dimensions for text-embedding-3-small)
        text: Raw text content of the chunk
        doc_id: Document identifier (e.g., "intro-ros2-ur")
        language: Language of the text chunk ("en", "ur", or "ja")
        original_language: Language of the source document
        translation_source: Source of translation ("original", "human", or "machine")
        content_type: Type of content ("ui", "docs", or "chat_context")
        translation_quality: Optional quality score (0.0-1.0) for translations
        chunk_index: Index of chunk within the document (0-based)
    """

    id: str
    vector: list[float]
    text: str
    doc_id: str
    language: LanguageCode
    original_language: LanguageCode
    translation_source: TranslationSource
    content_type: ContentType
    chunk_index: int
    translation_quality: float | None = None


@dataclass
class MultilingualSearchResult:
    """
    Result from a multilingual similarity search.

    Attributes:
        id: Point ID from Qdrant
        score: Similarity score (higher is more similar)
        text: Text content from payload
        doc_id: Document ID from payload
        language: Language of the result
        original_language: Original language of the document
        translation_source: Source of translation
        content_type: Type of content
        chunk_index: Chunk index from payload
        translation_quality: Optional translation quality score
    """

    id: str
    score: float
    text: str
    doc_id: str
    language: LanguageCode
    original_language: LanguageCode
    translation_source: TranslationSource
    content_type: ContentType
    chunk_index: int
    translation_quality: float | None = None


async def ensure_language_indexes(
    collection_name: str | None = None,
) -> None:
    """
    Create payload indexes for language-based filtering.

    This function creates indexes for language-related fields to enable
    efficient filtering in multilingual search queries.

    Indexes created:
    - language (KEYWORD): For language filtering
    - original_language (KEYWORD): For source language tracking
    - translation_source (KEYWORD): For filtering by translation type
    - content_type (KEYWORD): For filtering by content category

    Args:
        collection_name: Name of collection (defaults to settings.QDRANT_COLLECTION_NAME)

    Raises:
        Exception: If index creation fails

    Example:
        await ensure_language_indexes()
    """
    client = get_qdrant_client()
    collection_name = collection_name or settings.QDRANT_COLLECTION_NAME

    # Create language index (KEYWORD for exact matching)
    await client.create_payload_index(
        collection_name=collection_name,
        field_name="language",
        field_schema=PayloadSchemaType.KEYWORD,
    )

    # Create original_language index (KEYWORD for exact matching)
    await client.create_payload_index(
        collection_name=collection_name,
        field_name="original_language",
        field_schema=PayloadSchemaType.KEYWORD,
    )

    # Create translation_source index (KEYWORD for exact matching)
    await client.create_payload_index(
        collection_name=collection_name,
        field_name="translation_source",
        field_schema=PayloadSchemaType.KEYWORD,
    )

    # Create content_type index (KEYWORD for exact matching)
    await client.create_payload_index(
        collection_name=collection_name,
        field_name="content_type",
        field_schema=PayloadSchemaType.KEYWORD,
    )


async def index_document(
    doc_text: str,
    doc_id: str,
    language: LanguageCode,
    original_language: LanguageCode | None = None,
    translation_source: TranslationSource = "original",
    content_type: ContentType = "docs",
    translation_quality: float | None = None,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    collection_name: str | None = None,
) -> int:
    """
    Index a document with language metadata.

    This function:
    1. Splits the document into chunks
    2. Generates embeddings for each chunk
    3. Stores chunks in Qdrant with language metadata

    Args:
        doc_text: Full text of the document to index
        doc_id: Unique identifier for the document (e.g., "intro-ros2-ur")
        language: Language code of the document text ("en", "ur", or "ja")
        original_language: Language of the source document (defaults to same as language)
        translation_source: Source of translation ("original", "human", or "machine")
        content_type: Type of content ("ui", "docs", or "chat_context")
        translation_quality: Optional quality score (0.0-1.0) for translations
        chunk_size: Target size of each chunk in characters (default: 500)
        chunk_overlap: Number of overlapping characters between chunks (default: 50)
        collection_name: Name of collection (defaults to settings.QDRANT_COLLECTION_NAME)

    Returns:
        Number of chunks indexed

    Raises:
        ValueError: If doc_text is empty or invalid parameters
        Exception: If indexing fails

    Example:
        # Index original English document
        chunks_indexed = await index_document(
            doc_text="ROS 2 is a modern robotics framework...",
            doc_id="intro-ros2-en",
            language="en"
        )

        # Index human-translated Urdu document
        chunks_indexed = await index_document(
            doc_text="ROS 2 روبوٹکس سسٹم کے لیے ایک فریم ورک ہے...",
            doc_id="intro-ros2-ur",
            language="ur",
            original_language="en",
            translation_source="human",
            translation_quality=0.95
        )
    """
    # Validation
    if not doc_text or not doc_text.strip():
        raise ValueError("doc_text cannot be empty")

    if language not in ["en", "ur", "ja"]:
        raise ValueError(f"Invalid language: {language}. Must be 'en', 'ur', or 'ja'")

    if translation_quality is not None and not (0.0 <= translation_quality <= 1.0):
        raise ValueError(f"translation_quality must be between 0.0 and 1.0, got {translation_quality}")

    # Default original_language to language if not specified
    if original_language is None:
        original_language = language

    # Split document into chunks
    chunks_text = _split_into_chunks(doc_text, chunk_size, chunk_overlap)

    # Generate embeddings for all chunks
    embeddings = await batch_embed(chunks_text)

    # Create MultilingualEmbeddingChunk objects
    chunks = [
        MultilingualEmbeddingChunk(
            id=f"{doc_id}:{i}",
            vector=embedding,
            text=text,
            doc_id=doc_id,
            language=language,
            original_language=original_language,
            translation_source=translation_source,
            content_type=content_type,
            chunk_index=i,
            translation_quality=translation_quality,
        )
        for i, (text, embedding) in enumerate(zip(chunks_text, embeddings))
    ]

    # Upsert to Qdrant
    await _upsert_multilingual_chunks(chunks, collection_name)

    return len(chunks)


async def _upsert_multilingual_chunks(
    chunks: Sequence[MultilingualEmbeddingChunk],
    collection_name: str | None = None,
) -> None:
    """
    Internal function to upsert multilingual chunks to Qdrant.

    Args:
        chunks: List of MultilingualEmbeddingChunk objects to upsert
        collection_name: Name of collection (defaults to settings.QDRANT_COLLECTION_NAME)
    """
    if not chunks:
        raise ValueError("Chunks list cannot be empty")

    client = get_qdrant_client()
    collection_name = collection_name or settings.QDRANT_COLLECTION_NAME

    # Convert chunks to Qdrant points with language metadata
    points = [
        PointStruct(
            id=uuid4(),  # UUID for Qdrant
            vector=chunk.vector,
            payload={
                "chunk_id": chunk.id,  # Preserve meaningful identifier
                "text": chunk.text,
                "doc_id": chunk.doc_id,
                "language": chunk.language,
                "original_language": chunk.original_language,
                "translation_source": chunk.translation_source,
                "content_type": chunk.content_type,
                "chunk_index": chunk.chunk_index,
                "translation_quality": chunk.translation_quality,
            },
        )
        for chunk in chunks
    ]

    # Upsert to Qdrant
    await client.upsert(
        collection_name=collection_name,
        points=points,
    )


def _split_into_chunks(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[str]:
    """
    Split text into overlapping chunks.

    This is a simple character-based chunking strategy. For production,
    consider using more sophisticated methods like sentence-aware chunking
    or semantic chunking.

    Args:
        text: Text to split
        chunk_size: Target size of each chunk in characters
        chunk_overlap: Number of overlapping characters between chunks

    Returns:
        List of text chunks
    """
    if chunk_size <= chunk_overlap:
        raise ValueError("chunk_size must be greater than chunk_overlap")

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        # Calculate end position
        end = start + chunk_size

        # Extract chunk
        chunk = text[start:end]

        # Only add non-empty chunks
        if chunk.strip():
            chunks.append(chunk)

        # Move start position (with overlap)
        start += chunk_size - chunk_overlap

    return chunks


async def search_with_language_filter(
    query: str,
    language: LanguageCode,
    limit: int = 10,
    collection_name: str | None = None,
    content_type: ContentType | None = None,
    score_threshold: float | None = None,
) -> list[MultilingualSearchResult]:
    """
    Search for similar documents with language filtering.

    This function performs semantic search and filters results to only
    include documents in the specified language.

    Args:
        query: Search query text
        language: Language code to filter by ("en", "ur", or "ja")
        limit: Maximum number of results to return (default: 10)
        collection_name: Name of collection (defaults to settings.QDRANT_COLLECTION_NAME)
        content_type: Optional filter by content type ("ui", "docs", or "chat_context")
        score_threshold: Optional minimum similarity score (0-1 for cosine)

    Returns:
        List of MultilingualSearchResult objects, sorted by similarity (highest first)

    Raises:
        ValueError: If language is invalid

    Example:
        # Search for Urdu documents
        results = await search_with_language_filter(
            query="ROS 2 کیا ہے؟",
            language="ur",
            limit=5
        )

        # Search for English UI strings only
        results = await search_with_language_filter(
            query="Submit button",
            language="en",
            content_type="ui",
            limit=3
        )
    """
    # Import here to avoid circular dependency
    from app.services.embeddings import embed_query

    # Validation
    if language not in ["en", "ur", "ja"]:
        raise ValueError(f"Invalid language: {language}. Must be 'en', 'ur', or 'ja'")

    # Generate query embedding
    query_vector = await embed_query(query)

    # Use sync client for search
    sync_client = get_sync_qdrant_client()
    collection_name = collection_name or settings.QDRANT_COLLECTION_NAME

    # Build filter conditions
    filter_conditions = [
        FieldCondition(
            key="language",
            match=MatchValue(value=language),
        )
    ]

    # Add content_type filter if specified
    if content_type:
        filter_conditions.append(
            FieldCondition(
                key="content_type",
                match=MatchValue(value=content_type),
            )
        )

    # Build filter object
    query_filter = Filter(must=filter_conditions)

    # Query using sync client via asyncio.to_thread
    query_response = await asyncio.to_thread(
        sync_client.query_points,
        collection_name=collection_name,
        query=query_vector,
        query_filter=query_filter,
        limit=limit,
        with_payload=True,
        with_vectors=False,
        score_threshold=score_threshold,
    )

    # Extract points from response
    search_results = query_response.points

    # Convert to MultilingualSearchResult objects
    results = [
        MultilingualSearchResult(
            id=str(point.id),
            score=point.score,
            text=point.payload.get("text", ""),
            doc_id=point.payload.get("doc_id", ""),
            language=point.payload.get("language", "en"),
            original_language=point.payload.get("original_language", "en"),
            translation_source=point.payload.get("translation_source", "original"),
            content_type=point.payload.get("content_type", "docs"),
            chunk_index=point.payload.get("chunk_index", 0),
            translation_quality=point.payload.get("translation_quality"),
        )
        for point in search_results
    ]

    return results


async def search_with_fallback(
    query: str,
    primary_language: LanguageCode,
    fallback_language: LanguageCode = "en",
    limit: int = 10,
    min_results: int = 3,
    collection_name: str | None = None,
    content_type: ContentType | None = None,
) -> tuple[list[MultilingualSearchResult], bool]:
    """
    Search with language filtering and fallback to another language.

    If the primary language search returns fewer than min_results,
    this function will search again with the fallback language and
    merge the results.

    Args:
        query: Search query text
        primary_language: Primary language code to search ("en", "ur", or "ja")
        fallback_language: Fallback language code (default: "en")
        limit: Maximum number of results to return (default: 10)
        min_results: Minimum results before triggering fallback (default: 3)
        collection_name: Name of collection (defaults to settings.QDRANT_COLLECTION_NAME)
        content_type: Optional filter by content type

    Returns:
        Tuple of (results, fallback_applied) where:
        - results: List of MultilingualSearchResult objects
        - fallback_applied: True if fallback search was used

    Example:
        # Search for Urdu content, fall back to English if insufficient results
        results, used_fallback = await search_with_fallback(
            query="ROS 2 کیا ہے؟",
            primary_language="ur",
            fallback_language="en",
            limit=5,
            min_results=3
        )

        if used_fallback:
            print("Fallback to English content was applied")
    """
    # Search with primary language
    primary_results = await search_with_language_filter(
        query=query,
        language=primary_language,
        limit=limit,
        collection_name=collection_name,
        content_type=content_type,
    )

    # Check if we need fallback
    if len(primary_results) >= min_results:
        return primary_results, False

    # Search with fallback language
    fallback_results = await search_with_language_filter(
        query=query,
        language=fallback_language,
        limit=limit - len(primary_results),  # Get remaining needed results
        collection_name=collection_name,
        content_type=content_type,
    )

    # Merge results (primary first, then fallback)
    merged_results = primary_results + fallback_results

    return merged_results[:limit], True
