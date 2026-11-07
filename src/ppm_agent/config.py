"""Project configuration loaded from environment variables / a local .env file.

The source corpus is referenced by path (JSF_SOURCE_DIR) and is treated as read-only.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    jsf_source_dir: Path | None
    vector_store_dir: Path
    collection_name: str
    embedding_model: str
    chunk_size: int  # tokens (embedding-model tokenizer)
    chunk_overlap: int  # tokens
    top_k: int
    candidate_k: int  # candidates retrieved before duplicate suppression
    dedup_min_shared_words: int  # shared word run that marks two nearby chunks as duplicates
    openai_api_key: str | None
    openai_model: str
    metadata_dir: Path
    traces_dir: Path
    log_level: str


def get_settings() -> Settings:
    """Build a Settings object from the current environment."""
    source = os.getenv("JSF_SOURCE_DIR")
    return Settings(
        jsf_source_dir=Path(source) if source else None,
        # Relative paths are resolved against the project root; absolute paths are kept as-is.
        vector_store_dir=PROJECT_ROOT / os.getenv("VECTOR_STORE_DIR", "data/processed/chroma"),
        collection_name=os.getenv("CHROMA_COLLECTION", "jsf_corpus"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        chunk_size=int(os.getenv("CHUNK_SIZE_TOKENS", "220")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP_TOKENS", "35")),
        top_k=int(os.getenv("TOP_K", "5")),
        candidate_k=int(os.getenv("CANDIDATE_K", "15")),
        dedup_min_shared_words=int(os.getenv("DEDUP_MIN_SHARED_WORDS", "12")),
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        metadata_dir=PROJECT_ROOT / "data" / "metadata",
        traces_dir=PROJECT_ROOT / "outputs" / "retrieval_traces",
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
