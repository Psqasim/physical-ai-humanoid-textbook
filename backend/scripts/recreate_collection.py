"""
Recreate Qdrant collection with proper payload indexes.

This script:
1. Deletes the existing Qdrant collection (if it exists)
2. Creates a new collection with proper schema
3. Creates payload indexes for doc_path, chunk_index, module_id

CRITICAL: This fixes the "Index required but not found for 'doc_path'" error
that occurs when using selection-based Q&A mode.

After running this script, you must re-index the textbook content using:
    uv run python -m scripts.index_docs

Usage:
    # Recreate collection (DESTRUCTIVE - deletes all data!)
    uv run python -m scripts.recreate_collection

    # Dry run (show what would be done)
    uv run python -m scripts.recreate_collection --dry-run
"""

import asyncio
import sys
from pathlib import Path

# Add backend dir to path so we can import app modules
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


async def recreate_collection(dry_run: bool = False) -> None:
    """
    Recreate the Qdrant collection with proper payload indexes.

    Args:
        dry_run: If True, show what would be done without actually doing it
    """
    from app.core.logging import get_logger
    from app.core.config import settings
    from app.services.qdrant import (
        get_qdrant_client,
        ensure_collection_exists,
        create_payload_indexes,
    )

    logger = get_logger(__name__)

    logger.info("=" * 60)
    logger.info("Qdrant Collection Recreation Script")
    logger.info("=" * 60)
    logger.info(f"Collection name: {settings.QDRANT_COLLECTION_NAME}")
    logger.info(f"Qdrant URL: {settings.QDRANT_URL}")

    if dry_run:
        logger.info("")
        logger.info("DRY RUN MODE: No actual changes will be made")
        logger.info("")
        logger.info("Steps that would be performed:")
        logger.info("1. Check if collection exists")
        logger.info("2. Delete existing collection (if exists)")
        logger.info("3. Create new collection with vector config")
        logger.info("4. Create payload indexes:")
        logger.info("   - doc_path (KEYWORD)")
        logger.info("   - chunk_index (INTEGER)")
        logger.info("   - module_id (KEYWORD)")
        logger.info("")
        logger.info("To execute these steps, run without --dry-run flag:")
        logger.info("  uv run python -m scripts.recreate_collection")
        logger.info("=" * 60)
        return

    # Get client
    client = get_qdrant_client()

    # Step 1: Check if collection exists
    logger.info("")
    logger.info("Step 1: Checking if collection exists...")
    collections = await client.get_collections()
    existing_names = [col.name for col in collections.collections]

    if settings.QDRANT_COLLECTION_NAME in existing_names:
        logger.info(f"✓ Collection '{settings.QDRANT_COLLECTION_NAME}' exists")

        # Step 2: Delete existing collection
        logger.info("")
        logger.info("Step 2: Deleting existing collection...")
        logger.warning("⚠️  WARNING: This will delete ALL existing data!")
        logger.warning("⚠️  Press Ctrl+C in the next 5 seconds to cancel...")

        try:
            await asyncio.sleep(5)
        except KeyboardInterrupt:
            logger.info("")
            logger.info("Operation cancelled by user.")
            return

        await client.delete_collection(collection_name=settings.QDRANT_COLLECTION_NAME)
        logger.info(f"✓ Collection '{settings.QDRANT_COLLECTION_NAME}' deleted")
    else:
        logger.info(f"Collection '{settings.QDRANT_COLLECTION_NAME}' does not exist")

    # Step 3: Create new collection with indexes
    logger.info("")
    logger.info("Step 3: Creating new collection with proper schema...")
    created = await ensure_collection_exists(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        vector_size=1536,  # text-embedding-3-small dimension
    )

    if created:
        logger.info(f"✓ Collection '{settings.QDRANT_COLLECTION_NAME}' created")
        logger.info("✓ Payload indexes created:")
        logger.info("  - doc_path (KEYWORD)")
        logger.info("  - chunk_index (INTEGER)")
        logger.info("  - module_id (KEYWORD)")
    else:
        logger.error("✗ Failed to create collection")
        return

    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("Collection Recreation Complete!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Re-index the textbook content:")
    logger.info("   uv run python -m scripts.index_docs")
    logger.info("")
    logger.info("2. Test selection-based Q&A:")
    logger.info("   - Select text on a docs page")
    logger.info("   - Click 'Ask about this'")
    logger.info("   - Ask a question")
    logger.info("   - Backend should return 200 OK (not 400)")
    logger.info("")
    logger.info("=" * 60)


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Recreate Qdrant collection with proper payload indexes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (show what would be done)
  uv run python -m scripts.recreate_collection --dry-run

  # Recreate collection (DESTRUCTIVE!)
  uv run python -m scripts.recreate_collection

IMPORTANT: After recreating the collection, you MUST re-index:
  uv run python -m scripts.index_docs
        """,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it",
    )
    args = parser.parse_args()

    asyncio.run(recreate_collection(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
