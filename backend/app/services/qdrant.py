"""
Qdrant vector database client wrapper.

This module provides a high-level interface to Qdrant Cloud for:
- Collection management (create, ensure exists)
- Embedding storage (upsert)
- Similarity search (query)

The client is created lazily to avoid network calls during import.

Usage:
    from app.services.qdrant import (
        get_qdrant_client,
        ensure_collection_exists,
        upsert_embeddings,
        search_similar,
        EmbeddingChunk,
    )

    # Ensure collection exists
    await ensure_collection_exists()

    # Store embeddings
    chunks = [
        EmbeddingChunk(
            id="docs/intro.md:0",
            vector=[0.1, 0.2, ...],
            doc_path="docs/intro.md",
            module_id="1",
            heading="Introduction",
            chunk_index=0,
            text="This is the content..."
        )
    ]
    await upsert_embeddings(chunks)

    # Search similar
    results = await search_similar(
        query_vector=[0.1, 0.2, ...],
        limit=5,
        doc_path="docs/intro.md"  # Optional filter
    )
"""

from typing import Any, Sequence
from dataclasses import dataclass
from qdrant_client import QdrantClient, AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

from app.core.config import settings


# Global client instance (lazily initialized)
_client: AsyncQdrantClient | None = None


@dataclass
class EmbeddingChunk:
    """
    Data model for an embedding chunk.

    This matches the metadata structure defined in the spec for
    storing textbook chunks in Qdrant.

    Attributes:
        id: Unique identifier (format: "doc_path:chunk_index")
        vector: Embedding vector (1536 dimensions for text-embedding-3-small)
        doc_path: Relative path to source document (e.g., "docs/intro.md")
        module_id: Module identifier (e.g., "1", "2")
        heading: Section heading from the document
        chunk_index: Index of chunk within the document (0-based)
        text: Raw text content of the chunk
    """

    id: str
    vector: list[float]
    doc_path: str
    module_id: str
    heading: str
    chunk_index: int
    text: str


@dataclass
class SearchResult:
    """
    Result from a similarity search.

    Attributes:
        id: Point ID from Qdrant
        score: Similarity score (higher is more similar)
        doc_path: Document path from payload
        module_id: Module ID from payload
        heading: Section heading from payload
        chunk_index: Chunk index from payload
        text: Text content from payload
    """

    id: str
    score: float
    doc_path: str
    module_id: str
    heading: str
    chunk_index: int
    text: str


def get_qdrant_client() -> AsyncQdrantClient:
    """
    Get or create the Qdrant async client.

    The client is created once and reused for all operations.
    Uses URL and API key from settings.

    Returns:
        AsyncQdrantClient instance

    Raises:
        ValueError: If QDRANT_URL or QDRANT_API_KEY is not configured
    """
    global _client
    if _client is None:
        if not settings.QDRANT_URL:
            raise ValueError(
                "QDRANT_URL is not configured. "
                "Please set it in your environment variables or .env file."
            )
        if not settings.QDRANT_API_KEY:
            raise ValueError(
                "QDRANT_API_KEY is not configured. "
                "Please set it in your environment variables or .env file."
            )

        _client = AsyncQdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )
    return _client


async def ensure_collection_exists(
    collection_name: str | None = None,
    vector_size: int = 1536,
    distance: Distance = Distance.COSINE,
) -> bool:
    """
    Ensure the Qdrant collection exists, creating it if necessary.

    Args:
        collection_name: Name of collection (defaults to settings.QDRANT_COLLECTION_NAME)
        vector_size: Dimension of embedding vectors (default: 1536 for text-embedding-3-small)
        distance: Distance metric (default: COSINE)

    Returns:
        True if collection was created, False if it already existed

    Raises:
        Exception: If collection creation fails

    Example:
        created = await ensure_collection_exists()
        if created:
            print("Collection created successfully")
    """
    client = get_qdrant_client()
    collection_name = collection_name or settings.QDRANT_COLLECTION_NAME

    # Check if collection exists
    collections = await client.get_collections()
    existing_names = [col.name for col in collections.collections]

    if collection_name in existing_names:
        return False

    # Create collection
    await client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=distance,
        ),
    )
    return True


async def upsert_embeddings(
    chunks: Sequence[EmbeddingChunk],
    collection_name: str | None = None,
) -> None:
    """
    Upsert embedding chunks to Qdrant.

    Uses the chunk ID as the point ID, so existing chunks are updated
    and new chunks are inserted (idempotent operation).

    Args:
        chunks: List of EmbeddingChunk objects to upsert
        collection_name: Name of collection (defaults to settings.QDRANT_COLLECTION_NAME)

    Raises:
        ValueError: If chunks list is empty
        Exception: If upsert fails

    Example:
        chunks = [
            EmbeddingChunk(
                id="docs/intro.md:0",
                vector=[0.1, 0.2, ...],
                doc_path="docs/intro.md",
                module_id="1",
                heading="Introduction",
                chunk_index=0,
                text="Content here..."
            )
        ]
        await upsert_embeddings(chunks)
    """
    if not chunks:
        raise ValueError("Chunks list cannot be empty")

    client = get_qdrant_client()
    collection_name = collection_name or settings.QDRANT_COLLECTION_NAME

    # Convert chunks to Qdrant points
    points = [
        PointStruct(
            id=chunk.id,
            vector=chunk.vector,
            payload={
                "doc_path": chunk.doc_path,
                "module_id": chunk.module_id,
                "heading": chunk.heading,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
            },
        )
        for chunk in chunks
    ]

    # Upsert to Qdrant
    await client.upsert(
        collection_name=collection_name,
        points=points,
    )


async def search_similar(
    query_vector: list[float],
    limit: int = 10,
    collection_name: str | None = None,
    doc_path: str | None = None,
    module_id: str | None = None,
    score_threshold: float | None = None,
) -> list[SearchResult]:
    """
    Search for similar embeddings in Qdrant.

    Args:
        query_vector: Query embedding vector
        limit: Maximum number of results to return
        collection_name: Name of collection (defaults to settings.QDRANT_COLLECTION_NAME)
        doc_path: Optional filter by document path (exact match)
        module_id: Optional filter by module ID (exact match)
        score_threshold: Optional minimum similarity score (0-1 for cosine)

    Returns:
        List of SearchResult objects, sorted by similarity (highest first)

    Example:
        # Whole-book search
        results = await search_similar(query_vector, limit=5)

        # Selection-based search (filter by document)
        results = await search_similar(
            query_vector,
            limit=5,
            doc_path="docs/intro.md"
        )
    """
    client = get_qdrant_client()
    collection_name = collection_name or settings.QDRANT_COLLECTION_NAME

    # Build filter conditions
    filter_conditions = []
    if doc_path:
        filter_conditions.append(
            FieldCondition(
                key="doc_path",
                match=MatchValue(value=doc_path),
            )
        )
    if module_id:
        filter_conditions.append(
            FieldCondition(
                key="module_id",
                match=MatchValue(value=module_id),
            )
        )

    # Build filter object if we have conditions
    query_filter = Filter(must=filter_conditions) if filter_conditions else None

    # Search
    search_results = await client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=limit,
        query_filter=query_filter,
        score_threshold=score_threshold,
    )

    # Convert to SearchResult objects
    results = [
        SearchResult(
            id=str(hit.id),
            score=hit.score,
            doc_path=hit.payload.get("doc_path", ""),
            module_id=hit.payload.get("module_id", ""),
            heading=hit.payload.get("heading", ""),
            chunk_index=hit.payload.get("chunk_index", 0),
            text=hit.payload.get("text", ""),
        )
        for hit in search_results
    ]

    return results


async def delete_by_doc_path(
    doc_path: str,
    collection_name: str | None = None,
) -> None:
    """
    Delete all chunks for a specific document.

    Useful for removing outdated content before re-indexing a document.

    Args:
        doc_path: Document path to delete
        collection_name: Name of collection (defaults to settings.QDRANT_COLLECTION_NAME)

    Example:
        await delete_by_doc_path("docs/intro.md")
    """
    client = get_qdrant_client()
    collection_name = collection_name or settings.QDRANT_COLLECTION_NAME

    await client.delete(
        collection_name=collection_name,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="doc_path",
                    match=MatchValue(value=doc_path),
                )
            ]
        ),
    )


async def get_collection_info(
    collection_name: str | None = None,
) -> dict[str, Any]:
    """
    Get information about the collection.

    Args:
        collection_name: Name of collection (defaults to settings.QDRANT_COLLECTION_NAME)

    Returns:
        Dictionary with collection information (point count, vector config, etc.)

    Example:
        info = await get_collection_info()
        print(f"Collection has {info['points_count']} points")
    """
    client = get_qdrant_client()
    collection_name = collection_name or settings.QDRANT_COLLECTION_NAME

    collection = await client.get_collection(collection_name=collection_name)

    return {
        "name": collection_name,
        "points_count": collection.points_count,
        "vectors_count": collection.vectors_count,
        "status": collection.status,
    }
