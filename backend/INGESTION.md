# Document Ingestion Pipeline

Production-ready embedding ingestion system for the Physical AI & Humanoid Robotics Textbook RAG backend.

## Overview

This pipeline embeds **all documentation content** (English, Japanese, Urdu) and stores it in Qdrant for semantic search and retrieval.

### Features

- ✅ Reads docs from filesystem (docs/, i18n/ja/, i18n/ur/)
- ✅ Markdown/MDX-aware chunking (preserves headings)
- ✅ OpenAI embeddings (text-embedding-3-small)
- ✅ Language-aware metadata (en, ja, ur)
- ✅ Qdrant storage with indexes
- ✅ Idempotent re-ingestion support
- ✅ Comprehensive logging and error handling

## Prerequisites

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   # Create .env file in backend/
   cp .env.example .env
   ```

   Required variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `QDRANT_URL`: Qdrant cluster URL
   - `QDRANT_API_KEY`: Qdrant API key
   - `QDRANT_COLLECTION_NAME`: Collection name (default: `textbook_embeddings`)

## Usage

### Run Full Ingestion

From the **project root** (not backend/):

```bash
python -m backend.app.scripts.ingest_docs
```

Or from the **backend/** directory:

```bash
cd backend
python -m app.scripts.ingest_docs
```

### Command Options

- `--dry-run`: Preview without ingesting
  ```bash
  python -m backend.app.scripts.ingest_docs --dry-run
  ```

- `--project-root`: Specify project root path (auto-detected by default)
  ```bash
  python -m backend.app.scripts.ingest_docs --project-root /path/to/project
  ```

- `--collection`: Override collection name
  ```bash
  python -m backend.app.scripts.ingest_docs --collection my_collection
  ```

- `--force`: Force re-ingestion (TODO: implement collection deletion)
  ```bash
  python -m backend.app.scripts.ingest_docs --force
  ```

## Pipeline Steps

### 1. Document Discovery

Scans for `.md` and `.mdx` files in:
- `docs/` (English)
- `i18n/ja/docusaurus-plugin-content-docs/current/` (Japanese)
- `i18n/ur/docusaurus-plugin-content-docs/current/` (Urdu)

### 2. Metadata Extraction

From each file, extracts:
- **language**: `en`, `ja`, or `ur`
- **module**: e.g., `module-1`, `module-2`
- **chapter**: e.g., `chapter-1`, `overview`
- **source_path**: Relative path (e.g., `docs/intro.md`)
- **url_path**: GitHub Pages URL (e.g., `/docs/intro`)
- **title**: From frontmatter or filename

### 3. Chunking

Uses **markdown-aware chunking**:
- Preserves heading hierarchy
- Target: 500-800 tokens per chunk
- Overlap: 100 tokens between chunks
- Uses tiktoken (cl100k_base) for accurate token counting

### 4. Embedding Generation

- **Model**: `text-embedding-3-small` (1536 dimensions)
- **Batch size**: 100 texts per API call
- **Cost**: ~$0.0001 per 1K tokens
- **Total cost estimate**: ~$0.10-0.50 for full textbook

### 5. Qdrant Storage

**Batching**: Embeddings are upserted in batches of 100 to avoid Qdrant's batch size limits. Each batch has automatic retry logic if it fails.

**Collection Schema:**
```python
{
    # Point ID (not in payload): Canonical UUID string with dashes
    # Example: "5c56c793-69f3-4fbf-87e6-c4bf54c28c26"
    "vector": [0.1, 0.2, ...],           # 1536-dim embedding
    "raw_id": "docs/intro.md:0",         # Original ID for reference
    "doc_path": "docs/intro.md",          # Source file
    "module_id": "intro",                 # Module identifier
    "heading": "Introduction",            # Section heading
    "chunk_index": 0,                     # Chunk position
    "text": "...",                        # Chunk content
    "language": "en",                     # Document language
    "url_path": "/docs/intro"             # GitHub Pages URL
}
```

**Note on IDs**: Point IDs are deterministic UUIDs generated using `uuid.uuid5(NAMESPACE_DNS, "doc_path:chunk_index")`. This produces canonical 36-character UUID strings with dashes (e.g., `"5c56c793-69f3-4fbf-87e6-c4bf54c28c26"`) that Qdrant accepts. The same document chunk always gets the same UUID, enabling idempotent re-ingestion. The original ID is stored in the `raw_id` payload field for reference.

**Indexes Created:**
- `doc_path` (KEYWORD): For selection-based filtering
- `chunk_index` (INTEGER): For ordering chunks
- `module_id` (KEYWORD): For module filtering
- `language` (KEYWORD): For language-aware retrieval

## Output Example

```
============================================================
DOCUMENT INGESTION PIPELINE
============================================================
Project root:  /path/to/project
Collection:    textbook_embeddings
Model:         text-embedding-3-small
Dry run:       False
Force:         False
============================================================

📦 Setting up Qdrant collection...
✅ Collection 'textbook_embeddings' already exists
   Points in collection: 0

📖 Reading documentation files...
✅ Read 15 documents
   English:  12
   Japanese: 2
   Urdu:     1

✂️  Chunking documents...
✅ Created 87 chunks

🧠 Generating embeddings (batch size: 100)...
✅ Generated 87 embeddings

💾 Storing embeddings in Qdrant...
✅ Stored 87 embeddings
   Total points in collection: 87

============================================================
INGESTION SUMMARY
============================================================
Documents read:        15
Chunks created:        87
Embeddings generated:  87
Embeddings stored:     87
Errors:                0

By language:
  English:  72
  Japanese: 10
  Urdu:     5
============================================================
```

## Architecture

### File Structure

```
backend/app/
├── services/
│   ├── document_reader.py   # Read docs from filesystem
│   ├── chunker.py           # Markdown-aware chunking
│   ├── embeddings.py        # OpenAI embedding generation (existing)
│   └── qdrant.py            # Qdrant client wrapper (updated)
└── scripts/
    └── ingest_docs.py       # Main CLI script
```

### Data Flow

```
Filesystem (docs/, i18n/)
    ↓
document_reader.py (read + extract metadata)
    ↓
chunker.py (split into chunks)
    ↓
embeddings.py (generate vectors)
    ↓
qdrant.py (store in Qdrant)
    ↓
Qdrant Cloud (ready for retrieval)
```

## Testing

### Dry Run (No API Calls)

```bash
python -m backend.app.scripts.ingest_docs --dry-run
```

This will:
- Read all docs
- Chunk content
- Count tokens
- **NOT** call OpenAI or Qdrant

### Verify Collection

After ingestion, check Qdrant:

```bash
# From Python
from app.services.qdrant import get_collection_info
import asyncio

async def check():
    info = await get_collection_info()
    print(f"Points: {info['points_count']}")

asyncio.run(check())
```

## Troubleshooting

### ImportError: No module named 'tiktoken'

```bash
cd backend
pip install tiktoken==0.8.0
```

### ImportError: No module named 'frontmatter'

```bash
cd backend
pip install python-frontmatter==1.1.0
```

### OpenAI API Error: Rate limit

The pipeline batches requests (100 texts per call). If you hit rate limits:
- Wait 60 seconds
- Reduce batch size in `batch_embed()` call

### Qdrant Connection Error

Verify your `.env`:
```bash
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key
```

Test connection:
```bash
from app.services.qdrant import get_qdrant_client
client = get_qdrant_client()
```

## Re-Ingestion

To update embeddings after doc changes:

1. **Incremental** (upsert changed docs):
   - TODO: Implement change detection
   - Currently: Manual deletion of specific doc paths

2. **Full re-ingestion** (replace all):
   - TODO: Implement `--force` flag to delete collection first
   - Currently: Upserts will update existing chunks by UUID

## Performance

- **Reading docs**: <1 second for 50 files
- **Chunking**: <5 seconds for 50 docs
- **Embedding**: ~30 seconds for 100 chunks (batched)
- **Qdrant upsert**: ~2 seconds for 100 points

**Total time for ~100 chunks**: ~40 seconds

## Cost Estimate

**OpenAI Embeddings:**
- Model: `text-embedding-3-small`
- Price: $0.00002 per 1K tokens
- Average doc: 500 tokens/chunk
- 100 chunks: 50K tokens
- **Cost**: $0.001 per 100 chunks (~$1 for 100K chunks)

**Qdrant:**
- Free tier: 1GB storage
- ~6KB per vector (1536 dimensions + metadata)
- 100 vectors ≈ 600KB
- **Cost**: Free (well within limits)

## Next Steps

1. ✅ **Ingestion complete** - Run the script
2. ⏭️ **Update retrieval logic** - Modify `rag.py` to filter by language
3. ⏭️ **Test chat** - Verify language-aware responses
4. ⏭️ **Add change detection** - Only re-embed modified docs
5. ⏭️ **Monitor metrics** - Track embedding quality and search performance

## Support

For issues or questions:
1. Check logs in terminal output
2. Verify `.env` configuration
3. Test connection to OpenAI and Qdrant separately
4. Review error messages for specific failures
