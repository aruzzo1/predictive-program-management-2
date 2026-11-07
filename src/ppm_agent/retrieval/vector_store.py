"""Local persistent Chroma vector store.

Each record holds the chunk text (Chroma "document"), its embedding, and flat
metadata (document_id, filename, title, organization, pdf_page, printed_page, ...).
"""

from __future__ import annotations

from pathlib import Path

import chromadb

# Chroma limits how many records can be written per call.
UPSERT_BATCH_SIZE = 1000

# Keys stored as Chroma metadata (everything on a chunk except its text).
METADATA_KEYS = [
    "chunk_id",
    "document_id",
    "filename",
    "title",
    "organization",
    "publication_date",
    "publication_year",
    "publication_date_uncertain",
    "reporting_period",
    "content_not_before",
    "source_type",
    "document_hash",
    "pdf_page",
    "printed_page",
    "section_type",
    "extraction_quality",
    "chunk_index",
    "char_count",
    "token_count",
    "ingested_at",
]


def get_client(persist_dir: Path):
    """Open a persistent Chroma client rooted at ``persist_dir``."""
    persist_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(persist_dir))


def get_collection(client, name: str = "jsf_corpus"):
    """Open (or create) a collection that uses cosine distance."""
    return client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})


def reset_collection(client, name: str = "jsf_corpus"):
    """Delete and recreate the collection so ingestion is repeatable."""
    try:
        client.delete_collection(name)
    except Exception:
        pass  # collection did not exist yet
    return get_collection(client, name)


def to_chroma_metadata(chunk: dict) -> dict:
    """Chroma metadata must be str/int/float/bool, so missing (None) values are omitted."""
    return {k: chunk[k] for k in METADATA_KEYS if chunk.get(k) is not None}


def upsert_chunks(collection, chunks: list[dict], embeddings: list[list[float]]) -> None:
    """Insert or update chunks keyed by ``chunk_id``."""
    if len(chunks) != len(embeddings):
        raise ValueError("chunks and embeddings must be the same length")
    for start in range(0, len(chunks), UPSERT_BATCH_SIZE):
        batch = chunks[start : start + UPSERT_BATCH_SIZE]
        collection.upsert(
            ids=[c["chunk_id"] for c in batch],
            documents=[c["text"] for c in batch],
            embeddings=embeddings[start : start + UPSERT_BATCH_SIZE],
            metadatas=[to_chroma_metadata(c) for c in batch],
        )
