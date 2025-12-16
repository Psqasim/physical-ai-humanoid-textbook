"""
Document ingestion script for RAG backend.

Embeds all documentation content (English, Japanese, Urdu) and stores in Qdrant.

Usage:
    python -m app.scripts.ingest_docs

Options:
    --project-root: Path to project root (default: auto-detect)
    --collection: Qdrant collection name (default: from settings)
    --dry-run: Preview without actually ingesting
    --force: Force re-ingestion (delete existing data first)
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional
import argparse
import uuid

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root / "backend"))

from app.core.config import settings
from app.services.document_reader import read_all_documents, Document
from app.services.chunker import MarkdownChunker
from app.services.embeddings import batch_embed
from app.services.qdrant import (
    ensure_collection_exists,
    upsert_embeddings,
    get_collection_info,
    EmbeddingChunk,
)


class IngestionStats:
    """Track ingestion statistics."""

    def __init__(self):
        self.docs_read = 0
        self.chunks_created = 0
        self.embeddings_generated = 0
        self.embeddings_stored = 0
        self.errors = 0
        self.by_language = {"en": 0, "ja": 0, "ur": 0}

    def print_summary(self):
        """Print ingestion summary."""
        print("\n" + "=" * 60)
        print("INGESTION SUMMARY")
        print("=" * 60)
        print(f"Documents read:        {self.docs_read}")
        print(f"Chunks created:        {self.chunks_created}")
        print(f"Embeddings generated:  {self.embeddings_generated}")
        print(f"Embeddings stored:     {self.embeddings_stored}")
        print(f"Errors:                {self.errors}")
        print(f"\nBy language:")
        print(f"  English:  {self.by_language['en']}")
        print(f"  Japanese: {self.by_language['ja']}")
        print(f"  Urdu:     {self.by_language['ur']}")
        print("=" * 60)


async def ingest_documents(
    project_root: Path,
    collection_name: Optional[str] = None,
    dry_run: bool = False,
    force: bool = False,
) -> IngestionStats:
    """
    Main ingestion pipeline.

    Steps:
    1. Read all documentation files
    2. Chunk each document
    3. Generate embeddings in batches
    4. Store in Qdrant

    Args:
        project_root: Path to project root directory
        collection_name: Qdrant collection name (default: from settings)
        dry_run: If True, preview without ingesting
        force: If True, recreate collection (delete existing data)

    Returns:
        IngestionStats with summary
    """
    stats = IngestionStats()
    collection_name = collection_name or settings.QDRANT_COLLECTION_NAME

    print(f"\n{'=' * 60}")
    print(f"DOCUMENT INGESTION PIPELINE")
    print(f"{'=' * 60}")
    print(f"Project root:  {project_root}")
    print(f"Collection:    {collection_name}")
    print(f"Model:         {settings.OPENAI_EMBEDDING_MODEL}")
    print(f"Dry run:       {dry_run}")
    print(f"Force:         {force}")
    print(f"{'=' * 60}\n")

    # Step 1: Ensure collection exists
    if not dry_run:
        print("📦 Setting up Qdrant collection...")
        try:
            # TODO: Add force delete logic here if needed
            created = await ensure_collection_exists(collection_name=collection_name)
            if created:
                print(f"✅ Created collection '{collection_name}'")
            else:
                print(f"✅ Collection '{collection_name}' already exists")

            # Get collection info
            info = await get_collection_info(collection_name=collection_name)
            print(f"   Points in collection: {info['points_count']}")
        except Exception as e:
            print(f"❌ Failed to set up collection: {e}")
            stats.errors += 1
            return stats

    # Step 2: Read all documents
    print(f"\n📖 Reading documentation files...")
    try:
        documents = read_all_documents(project_root)
        stats.docs_read = len(documents)
        print(f"✅ Read {len(documents)} documents")

        # Count by language
        for doc in documents:
            stats.by_language[doc.metadata.language] += 1

        print(f"   English:  {stats.by_language['en']}")
        print(f"   Japanese: {stats.by_language['ja']}")
        print(f"   Urdu:     {stats.by_language['ur']}")
    except Exception as e:
        print(f"❌ Failed to read documents: {e}")
        stats.errors += 1
        return stats

    # Step 3: Chunk documents
    print(f"\n✂️  Chunking documents...")
    chunker = MarkdownChunker(chunk_size=700, chunk_overlap=100)
    all_chunks = []

    for doc in documents:
        try:
            text_chunks = chunker.chunk_document(doc.content)

            # Convert to EmbeddingChunk format (without vectors yet)
            for chunk in text_chunks:
                # Create a deterministic UUID from "doc_path:chunk_index"
                # uuid.uuid5 generates a canonical UUID (with dashes) from a namespace + name
                # This ensures Qdrant compatibility while being reproducible for re-ingestion
                raw_id = f"{doc.metadata.source_path}:{chunk.chunk_index}"
                deterministic_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, raw_id))  # Canonical UUID with dashes

                embedding_chunk = {
                    "id": deterministic_uuid,  # Canonical UUID string (e.g., "5c56c793-69f3-4fbf-87e6-c4bf54c28c26")
                    "raw_id": raw_id,  # Store original ID in payload for reference
                    "doc_path": doc.metadata.source_path,
                    "module_id": doc.metadata.module,
                    "heading": chunk.heading,
                    "chunk_index": chunk.chunk_index,
                    "text": chunk.text,
                    "language": doc.metadata.language,
                    "url_path": doc.metadata.url_path,
                }
                all_chunks.append(embedding_chunk)

        except Exception as e:
            print(f"⚠️  Failed to chunk {doc.metadata.source_path}: {e}")
            stats.errors += 1

    stats.chunks_created = len(all_chunks)
    print(f"✅ Created {len(all_chunks)} chunks")

    if dry_run:
        print(f"\n🔍 DRY RUN - Would generate {len(all_chunks)} embeddings")
        stats.print_summary()
        return stats

    # Step 4: Generate embeddings in batches
    print(f"\n🧠 Generating embeddings (batch size: 100)...")
    try:
        # Extract texts for embedding
        texts = [chunk["text"] for chunk in all_chunks]

        # Generate embeddings in batches
        embeddings = await batch_embed(texts, batch_size=100)
        stats.embeddings_generated = len(embeddings)
        print(f"✅ Generated {len(embeddings)} embeddings")

        # Attach embeddings to chunks
        for i, embedding in enumerate(embeddings):
            all_chunks[i]["vector"] = embedding

    except Exception as e:
        print(f"❌ Failed to generate embeddings: {e}")
        stats.errors += 1
        return stats

    # Step 5: Store in Qdrant (in batches)
    print(f"\n💾 Storing embeddings in Qdrant...")
    try:
        # Convert to EmbeddingChunk objects
        embedding_chunks = [
            EmbeddingChunk(
                id=chunk["id"],
                vector=chunk["vector"],
                doc_path=chunk["doc_path"],
                module_id=chunk["module_id"],
                heading=chunk["heading"],
                chunk_index=chunk["chunk_index"],
                text=chunk["text"],
                language=chunk["language"],
                url_path=chunk["url_path"],
                raw_id=chunk["raw_id"],
            )
            for chunk in all_chunks
        ]

        # Upsert in batches to avoid Qdrant batch size limits
        batch_size = 100
        total_batches = (len(embedding_chunks) + batch_size - 1) // batch_size

        for i in range(0, len(embedding_chunks), batch_size):
            batch = embedding_chunks[i:i + batch_size]
            batch_num = (i // batch_size) + 1

            try:
                await upsert_embeddings(batch, collection_name=collection_name)
                print(f"   Batch {batch_num}/{total_batches}: Stored {len(batch)} embeddings")
                stats.embeddings_stored += len(batch)
            except Exception as batch_error:
                print(f"   ⚠️  Batch {batch_num}/{total_batches} failed: {batch_error}")
                print(f"      Retrying batch {batch_num}...")
                try:
                    # Retry once
                    await upsert_embeddings(batch, collection_name=collection_name)
                    print(f"   ✅ Batch {batch_num}/{total_batches}: Stored {len(batch)} embeddings (retry successful)")
                    stats.embeddings_stored += len(batch)
                except Exception as retry_error:
                    print(f"   ❌ Batch {batch_num}/{total_batches} failed again: {retry_error}")
                    stats.errors += 1

        print(f"✅ Stored {stats.embeddings_stored} embeddings total")

        # Get final collection info
        info = await get_collection_info(collection_name=collection_name)
        print(f"   Total points in collection: {info['points_count']}")

    except Exception as e:
        import traceback
        print(f"❌ Failed to store embeddings: {e}")
        print(f"   Error details: {traceback.format_exc()}")
        stats.errors += 1
        return stats

    return stats


async def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Ingest documentation into RAG backend")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Path to project root (default: auto-detect)",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default=None,
        help="Qdrant collection name (default: from settings)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without actually ingesting",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-ingestion (delete existing data first)",
    )

    args = parser.parse_args()

    # Auto-detect project root if not provided
    if args.project_root is None:
        # Assume script is in backend/app/scripts/
        args.project_root = Path(__file__).resolve().parents[3]

    # Run ingestion
    stats = await ingest_documents(
        project_root=args.project_root,
        collection_name=args.collection,
        dry_run=args.dry_run,
        force=args.force,
    )

    # Print summary
    stats.print_summary()

    # Exit with error code if there were errors
    if stats.errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
