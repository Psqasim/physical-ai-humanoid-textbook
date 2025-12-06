#!/usr/bin/env python3
"""
Verification script to test that configuration loads correctly.

This script can be run without real API keys to verify that:
1. Settings class loads from environment variables
2. Logging is configured correctly
3. Dependency injection helpers work

Usage:
    # Set minimal required env vars
    export OPENAI_API_KEY="test-key"
    export QDRANT_URL="https://test.qdrant.io"
    export QDRANT_API_KEY="test-key"
    export DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db"

    # Run verification
    uv run python verify_config.py
"""

import sys
import os

# Set dummy environment variables if not set (for testing only)
if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = "test-openai-key"
if "QDRANT_URL" not in os.environ:
    os.environ["QDRANT_URL"] = "https://test.qdrant.io"
if "QDRANT_API_KEY" not in os.environ:
    os.environ["QDRANT_API_KEY"] = "test-qdrant-key"
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost/testdb"


def test_config():
    """Test that configuration loads correctly."""
    print("Testing configuration loading...")

    from app.core.config import get_settings, settings

    # Test that settings loads
    s = get_settings()
    print(f"✓ Settings loaded successfully")

    # Test required fields
    assert s.OPENAI_API_KEY, "OPENAI_API_KEY not set"
    assert s.QDRANT_URL, "QDRANT_URL not set"
    assert s.QDRANT_API_KEY, "QDRANT_API_KEY not set"
    assert s.DATABASE_URL, "DATABASE_URL not set"
    print(f"✓ All required fields present")

    # Test defaults
    assert s.OPENAI_EMBEDDING_MODEL == "text-embedding-3-small"
    assert s.OPENAI_CHAT_MODEL == "gpt-4o-mini"
    assert s.QDRANT_COLLECTION_NAME == "textbook_embeddings"
    assert s.MAX_QUESTION_TOKENS == 500
    assert s.CHUNK_RETRIEVAL_LIMIT == 10
    assert s.LOG_LEVEL == "INFO"
    print(f"✓ Default values correct")

    # Test cors_origins_list property
    origins = s.cors_origins_list
    assert isinstance(origins, list)
    assert len(origins) > 0
    print(f"✓ CORS origins parsed correctly: {origins}")

    # Test that cached instance works
    assert get_settings() is get_settings()
    print(f"✓ Settings caching works (lru_cache)")

    # Test direct import
    assert settings is s
    print(f"✓ Direct settings import works")


def test_logging():
    """Test that logging is configured correctly."""
    print("\nTesting logging configuration...")

    from app.core.logging import setup_logging, get_logger, log_config_on_startup

    # Test logger setup
    logger = setup_logging()
    assert logger is not None
    print(f"✓ Logger setup successful")

    # Test get_logger
    module_logger = get_logger("test_module")
    assert module_logger is not None
    print(f"✓ get_logger works")

    # Test logging output
    logger.info("Test info message")
    logger.debug("Test debug message")
    print(f"✓ Logging output works")

    # Test config logging
    print("\nConfiguration summary:")
    log_config_on_startup()


def test_deps():
    """Test that dependency injection helpers are available."""
    print("\nTesting dependency injection...")

    from app.core.deps import (
        get_settings,
        get_db,
        get_qdrant_client,
        get_openai_client,
        SettingsDep,
    )

    # Test get_settings dependency
    s = get_settings()
    assert s is not None
    print(f"✓ get_settings dependency works")

    # Test that placeholder deps raise NotImplementedError
    try:
        get_db()
        assert False, "get_db should raise NotImplementedError"
    except NotImplementedError as e:
        print(f"✓ get_db placeholder raises NotImplementedError (expected)")

    try:
        get_qdrant_client()
        assert False, "get_qdrant_client should raise NotImplementedError"
    except NotImplementedError as e:
        print(f"✓ get_qdrant_client placeholder raises NotImplementedError (expected)")

    try:
        get_openai_client()
        assert False, "get_openai_client should raise NotImplementedError"
    except NotImplementedError as e:
        print(f"✓ get_openai_client placeholder raises NotImplementedError (expected)")

    print(f"✓ All dependency stubs present")


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Backend Configuration Verification")
    print("=" * 60)

    try:
        test_config()
        test_logging()
        test_deps()

        print("\n" + "=" * 60)
        print("✅ All verification tests passed!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Copy .env.example to .env")
        print("2. Add real API keys and credentials to .env")
        print("3. Proceed to Phase 3 (Health Endpoint)")

        return 0

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Verification failed: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
