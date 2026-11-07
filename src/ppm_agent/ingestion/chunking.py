"""Structure-aware, token-aware chunking.

Hierarchy, from coarse to fine:
  1. page (a chunk never spans two pages, so every chunk has one exact pdf_page);
  2. section segment (Highlights text is never mixed with non-Highlights text);
  3. paragraphs - consecutive paragraphs are packed together up to chunk_size;
  4. sentences - only a paragraph longer than the limit is split, at sentence ends;
  5. words - only a single sentence longer than the limit is split by words.

Sizes are measured with ``length_fn``. Ingestion passes the embedding model's
tokenizer, so chunk_size and chunk_overlap are in tokens; the default (len)
measures characters, which keeps the unit tests independent of any model.

Overlap: each chunk after the first in a segment starts with the last full
sentence(s) of the previous chunk, up to chunk_overlap units.

``max_length`` is a hard ceiling: no chunk is ever longer than it (for example
the model's maximum input length), even after the small-tail merge.
"""

from __future__ import annotations

import re
from typing import Callable

MIN_CHUNK_CHARS = 50     # smaller pieces are dropped (stray labels, page numbers)
SMALL_TAIL_SHARE = 0.25  # a final piece below this share of chunk_size is merged into the previous chunk when it fits
TAIL_MERGE_SLACK = 1.15  # ... as long as the merged chunk stays within chunk_size * slack (and max_length)

SENTENCE_SPLIT = re.compile(r"(?<=[.!?”\"])\s+(?=[A-Z0-9“\"(•])")

LengthFn = Callable[[str], int]


def split_sentences(text: str) -> list[str]:
    return [s for s in SENTENCE_SPLIT.split(text) if s.strip()]


def split_long_text(text: str, limit: int, length_fn: LengthFn = len) -> list[str]:
    """Split text longer than ``limit`` at sentence boundaries (words as a last resort)."""
    if length_fn(text) <= limit:
        return [text]
    pieces, current = [], ""
    for sentence in split_sentences(text):
        if length_fn(sentence) > limit:  # one very long sentence: fall back to words
            if current:
                pieces.append(current)
                current = ""
            buf = ""
            for w in sentence.split():
                candidate = f"{buf} {w}" if buf else w
                if buf and length_fn(candidate) > limit:
                    pieces.append(buf)
                    buf = w
                else:
                    buf = candidate
            current = buf
        else:
            candidate = f"{current} {sentence}" if current else sentence
            if current and length_fn(candidate) > limit:
                pieces.append(current)
                current = sentence
            else:
                current = candidate
    if current:
        pieces.append(current)
    return pieces


def overlap_tail(text: str, overlap: int, length_fn: LengthFn = len) -> str:
    """Last whole sentence(s) of ``text`` that fit in ``overlap`` units.

    If even the last sentence is longer, use its last words that fit.
    """
    if overlap <= 0:
        return ""
    tail = ""
    for sentence in reversed(split_sentences(text)):
        candidate = f"{sentence} {tail}".strip()
        if length_fn(candidate) > overlap:
            break
        tail = candidate
    if not tail:
        words = text.split()
        for i in range(len(words) - 1, -1, -1):
            candidate = " ".join(words[i:])
            if length_fn(candidate) > overlap:
                break
            tail = candidate
    return tail.strip()


def pack_paragraphs(
    paragraphs: list[str],
    chunk_size: int,
    chunk_overlap: int,
    length_fn: LengthFn = len,
    max_length: int | None = None,
) -> list[str]:
    """Pack paragraphs into chunks of at most ``chunk_size`` units, with overlap."""
    # Any paragraph longer than the room left after the overlap is pre-split by sentence.
    room = chunk_size - chunk_overlap
    pieces = [p for para in paragraphs for p in split_long_text(para, room, length_fn)]

    chunks: list[str] = []
    current = ""
    new_parts: list[str] = []  # pieces added to the current chunk (excluding the overlap tail)
    for piece in pieces:
        candidate = f"{current}\n\n{piece}" if current else piece
        if current and length_fn(candidate) > chunk_size:
            chunks.append(current)
            tail = overlap_tail(current, chunk_overlap, length_fn)
            current = f"{tail}\n\n{piece}" if tail else piece
            new_parts = [piece]
        else:
            current = candidate
            new_parts.append(piece)
    if current:
        # merge a very small final piece into the previous chunk if it still fits
        new_text = "\n\n".join(new_parts)
        merge_limit = int(chunk_size * TAIL_MERGE_SLACK)
        if max_length is not None:
            merge_limit = min(merge_limit, max_length)
        merged = f"{chunks[-1]}\n\n{new_text}" if chunks else ""
        if chunks and length_fn(new_text) < SMALL_TAIL_SHARE * chunk_size and length_fn(merged) <= merge_limit:
            chunks[-1] = merged
        else:
            chunks.append(current)

    # hard ceiling: re-split anything that still exceeds max_length (should be rare)
    if max_length is not None:
        chunks = [p for c in chunks for p in split_long_text(c, max_length, length_fn)]
    return [c for c in chunks if len(c) >= MIN_CHUNK_CHARS]


def make_chunk_id(document_id: str, pdf_page: int, index: int) -> str:
    """Readable, stable ID, e.g. 'GAO-10-382-p031-c01'."""
    return f"{document_id}-p{pdf_page:03d}-c{index:02d}"


def chunk_pages(
    pages,
    doc_metadata: dict,
    chunk_size: int = 1200,
    chunk_overlap: int = 175,
    length_fn: LengthFn = len,
    max_length: int | None = None,
) -> list[dict]:
    """Chunk extracted pages of one document.

    Args:
        pages: ExtractedPage objects (or anything with pdf_page, printed_page,
            extraction_quality, paragraphs=[{"text", "section_type"}], skipped_reason).
        doc_metadata: document-level fields copied onto every chunk
            (document_id, filename, title, organization, publication_date, ...).
        chunk_size / chunk_overlap: in the units of ``length_fn``.
        length_fn: text -> size (tokens when a tokenizer counter is passed).
        max_length: hard per-chunk ceiling in the same units.
    """
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks = []
    for page in pages:
        if page.skipped_reason or not page.paragraphs:
            continue
        # split the page into runs of paragraphs with the same section_type
        segments: list[tuple[str | None, list[str]]] = []
        for para in page.paragraphs:
            if segments and segments[-1][0] == para["section_type"]:
                segments[-1][1].append(para["text"])
            else:
                segments.append((para["section_type"], [para["text"]]))

        index = 0
        for section_type, texts in segments:
            for text in pack_paragraphs(texts, chunk_size, chunk_overlap, length_fn, max_length):
                chunks.append(
                    {
                        **doc_metadata,
                        "chunk_id": make_chunk_id(doc_metadata["document_id"], page.pdf_page, index),
                        "text": text,
                        "pdf_page": page.pdf_page,
                        "printed_page": page.printed_page,
                        "section_type": section_type,
                        "extraction_quality": page.extraction_quality,
                        "chunk_index": index,
                        "char_count": len(text),
                        "token_count": length_fn(text) if length_fn is not len else None,
                    }
                )
                index += 1
    return chunks
