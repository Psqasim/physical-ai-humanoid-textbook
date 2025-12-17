"""
Document reader service for Docusaurus markdown files.

Reads documentation files from the filesystem, supporting:
- English docs (docs/)
- Japanese translations (i18n/ja/docusaurus-plugin-content-docs/current/)
- Urdu translations (i18n/ur/docusaurus-plugin-content-docs/current/)

Extracts metadata from file paths and frontmatter.
"""

import os
import re
from pathlib import Path
from typing import Literal
from dataclasses import dataclass
import frontmatter


@dataclass
class DocMetadata:
    """
    Metadata extracted from a documentation file.

    Attributes:
        language: Document language (en, ja, ur)
        module: Module identifier (e.g., "module-1", "module-2")
        chapter: Chapter identifier (e.g., "chapter-1", "overview")
        source_path: Relative path from project root
        url_path: URL path for GitHub Pages routing
        title: Document title from frontmatter
    """
    language: Literal["en", "ja", "ur"]
    module: str
    chapter: str
    source_path: str
    url_path: str
    title: str


@dataclass
class Document:
    """
    A documentation file with content and metadata.

    Attributes:
        content: Raw markdown content (without frontmatter)
        metadata: Document metadata
    """
    content: str
    metadata: DocMetadata


def discover_docs(project_root: Path) -> list[Path]:
    """
    Discover all documentation files in the project.

    Searches in:
    - docs/ (English)
    - i18n/ja/docusaurus-plugin-content-docs/current/ (Japanese)
    - i18n/ur/docusaurus-plugin-content-docs/current/ (Urdu)

    Args:
        project_root: Path to project root directory

    Returns:
        List of absolute paths to .md and .mdx files
    """
    doc_paths = []

    # English docs
    en_docs_dir = project_root / "docs"
    if en_docs_dir.exists():
        doc_paths.extend(en_docs_dir.rglob("*.md"))
        doc_paths.extend(en_docs_dir.rglob("*.mdx"))

    # Japanese docs
    ja_docs_dir = project_root / "i18n" / "ja" / "docusaurus-plugin-content-docs" / "current"
    if ja_docs_dir.exists():
        doc_paths.extend(ja_docs_dir.rglob("*.md"))
        doc_paths.extend(ja_docs_dir.rglob("*.mdx"))

    # Urdu docs
    ur_docs_dir = project_root / "i18n" / "ur" / "docusaurus-plugin-content-docs" / "current"
    if ur_docs_dir.exists():
        doc_paths.extend(ur_docs_dir.rglob("*.md"))
        doc_paths.extend(ur_docs_dir.rglob("*.mdx"))

    return sorted(doc_paths)


def extract_metadata(file_path: Path, project_root: Path) -> DocMetadata:
    """
    Extract metadata from file path and frontmatter.

    Args:
        file_path: Absolute path to documentation file
        project_root: Path to project root directory

    Returns:
        DocMetadata with extracted information

    Example:
        Path: /project/docs/module-1-ros2/chapter-1-basics.mdx
        -> language: "en"
        -> module: "module-1"
        -> chapter: "chapter-1"
        -> source_path: "docs/module-1-ros2/chapter-1-basics.mdx"
        -> url_path: "/docs/module-1-ros2/chapter-1-basics"
    """
    # Get relative path from project root
    relative_path = file_path.relative_to(project_root)
    source_path = str(relative_path).replace("\\", "/")  # Normalize path separators

    # Detect language from path
    if "i18n/ja/" in source_path:
        language = "ja"
        # Remove i18n prefix for URL path
        url_base = source_path.replace("i18n/ja/docusaurus-plugin-content-docs/current/", "")
    elif "i18n/ur/" in source_path:
        language = "ur"
        url_base = source_path.replace("i18n/ur/docusaurus-plugin-content-docs/current/", "")
    else:
        language = "en"
        url_base = source_path

    # Build URL path (remove file extension, add /docs prefix if not present)
    url_path = "/" + url_base.rsplit(".", 1)[0]  # Remove .md or .mdx
    if not url_path.startswith("/docs/"):
        if url_path == "/intro":
            url_path = "/docs/intro"
        elif not url_path.startswith("/"):
            url_path = "/docs/" + url_path

    # Extract module and chapter from path
    # Example: docs/module-1-ros2/chapter-1-basics.mdx
    # -> module: "module-1", chapter: "chapter-1"
    parts = relative_path.parts

    module = "intro"
    chapter = "intro"

    for part in parts:
        if part.startswith("module-"):
            module = part.split("-")[0] + "-" + part.split("-")[1]  # "module-1"
        if part.startswith("chapter-") or part == "overview.mdx" or part == "overview.md":
            if part == "overview.mdx" or part == "overview.md":
                chapter = "overview"
            else:
                chapter = part.split("-")[0] + "-" + part.split("-")[1]  # "chapter-1"

    # Read frontmatter for title
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
            title = post.get("title", file_path.stem)
    except Exception:
        title = file_path.stem

    return DocMetadata(
        language=language,
        module=module,
        chapter=chapter,
        source_path=source_path,
        url_path=url_path,
        title=title,
    )


def read_document(file_path: Path, project_root: Path) -> Document:
    """
    Read a documentation file and extract content and metadata.

    Args:
        file_path: Absolute path to documentation file
        project_root: Path to project root directory

    Returns:
        Document with content and metadata

    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If file encoding is invalid
    """
    with open(file_path, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)

    metadata = extract_metadata(file_path, project_root)
    content = post.content  # Content without frontmatter

    return Document(content=content, metadata=metadata)


def read_all_documents(project_root: Path) -> list[Document]:
    """
    Read all documentation files in the project.

    Args:
        project_root: Path to project root directory

    Returns:
        List of Document objects
    """
    doc_paths = discover_docs(project_root)
    documents = []

    for doc_path in doc_paths:
        try:
            doc = read_document(doc_path, project_root)
            documents.append(doc)
        except Exception as e:
            print(f"Warning: Failed to read {doc_path}: {e}")

    return documents
