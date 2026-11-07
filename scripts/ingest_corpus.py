"""Build the vector store from the documents of a corpus manifest.

Pipeline:
  source discovery + duplicate detection (whole folder, read-only)
  → corpus selection (manifest + corpus decisions + SHA-256; page ranges where the manifest sets them)
  → page extraction and cleaning (pypdf), including retrieval-hygiene rules
    (every removal logged to data/processed/<stem>_filtered_text.jsonl)
  → structure-aware chunking
  → local embeddings (sentence-transformers)
  → persistent Chroma store under data/processed/chroma/

Manifests:
  data/metadata/prototype_corpus.json   prototype_v1 (5 documents)   → outputs named prototype_*
  data/metadata/expanded_corpus_v2.json rag_expanded_v2 (10 documents) → outputs named expanded_v2_*

The source directory (JSF_SOURCE_DIR in .env) is only read, never modified.
Each run rebuilds the collection from scratch so results are reproducible.

Usage:
    python scripts/ingest_corpus.py
    python scripts/ingest_corpus.py --manifest data/metadata/expanded_corpus_v2.json
"""

from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from ppm_agent.config import PROJECT_ROOT, get_settings
from ppm_agent.ingestion.chunking import chunk_pages
from ppm_agent.ingestion.corpus_selection import MANIFEST_PATH, select_manifest_documents
from ppm_agent.ingestion.loaders import deduplicate, discover_documents
from ppm_agent.ingestion.page_extraction import extract_document
from ppm_agent.retrieval.embeddings import embed_texts, get_embedding_model, max_input_tokens, token_counter
from ppm_agent.retrieval.vector_store import get_client, reset_collection, upsert_chunks
from ppm_agent.utils.logging_utils import get_logger

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def short_org(organization: str) -> str:
    """'U.S. Government Accountability Office (GAO)' -> 'GAO' (the full name stays in the metadata)."""
    return organization.rsplit("(", 1)[-1].rstrip(")")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH, help="corpus manifest (default: prototype_v1)")
    args = parser.parse_args()
    manifest_path = args.manifest if args.manifest.is_absolute() else PROJECT_ROOT / args.manifest

    settings = get_settings()
    log = get_logger("ingest", settings.log_level)
    if settings.jsf_source_dir is None:
        raise SystemExit("JSF_SOURCE_DIR is not set. Copy .env.example to .env and set it.")
    start = time.time()
    ingested_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # 1-2. Discovery and exact-duplicate detection over the whole source folder (read-only)
    discovered = discover_documents(settings.jsf_source_dir)
    unique, duplicates = deduplicate(discovered)
    skipped_names = {d.skipped for d in duplicates}

    # 3. Corpus selection: only manifest documents with an allowed decision and matching hash
    manifest, docs = select_manifest_documents(settings.jsf_source_dir, manifest_path)
    stem = manifest.get("output_stem", "prototype")
    for doc in docs:
        if doc.filename in skipped_names:
            raise SystemExit(f"{doc.filename} is an exact duplicate and must not be ingested")
    log.info("Selected %d documents from %s (%s)", len(docs), manifest_path.name, manifest.get("manifest_version"))

    # 4-5. Extract pages and chunk (sizes measured in tokens of the embedding model's tokenizer)
    count_tokens = token_counter(settings.embedding_model)
    max_tokens = max_input_tokens(settings.embedding_model)
    all_chunks, per_doc, page_log, warnings, filtered = [], [], [], [], []
    hygiene_lines = Counter()
    for doc in docs:
        pages = extract_document(doc)
        chunks = chunk_pages(pages, doc.chunk_metadata(), settings.chunk_size, settings.chunk_overlap,
                             length_fn=count_tokens, max_length=max_tokens)
        for c in chunks:
            c["ingested_at"] = ingested_at
        all_chunks.extend(chunks)

        indexed = [p for p in pages if not p.skipped_reason]
        skipped = [p for p in pages if p.skipped_reason]
        degraded = [p.pdf_page for p in indexed if p.extraction_quality != "clean"]
        doc_hygiene = Counter()
        for p in pages:
            for r in p.removed:
                filtered.append({"document_id": doc.document_id, "pdf_page": p.pdf_page, **r})
                doc_hygiene[r["rule"]] += len(r["text"].split("\n"))  # one removed line or sentence per row
        hygiene_lines.update(doc_hygiene)
        per_doc.append(
            {
                "document_id": doc.document_id,
                "organization": doc.organization,
                "pdf_pages_considered": len(pages),
                "pdf_pages_indexed": len(indexed),
                "pdf_pages_skipped": len(skipped),
                "degraded_pages": degraded,
                "chunks": len(chunks),
                "highlights_chunks": sum(1 for c in chunks if c["section_type"] == "highlights"),
                "avg_chunk_chars": round(sum(c["char_count"] for c in chunks) / max(len(chunks), 1)),
                "avg_chunk_tokens": round(sum(c["token_count"] for c in chunks) / max(len(chunks), 1)),
                "agency_comments_chunks": sum(1 for c in chunks if c["section_type"] == "agency_comments"),
                "hygiene_removed": dict(sorted(doc_hygiene.items())),
                "publication_date": doc.publication_date,
                "publication_year": doc.publication_year,
                "publication_date_review_flag": doc.publication_date_review_flag,
                "reporting_period": doc.reporting_period,
                "content_not_before": doc.content_not_before,
            }
        )
        for p in pages:
            page_log.append(
                {
                    "document_id": doc.document_id,
                    "pdf_page": p.pdf_page,
                    "printed_page": p.printed_page,
                    "indexed": not p.skipped_reason,
                    "skipped_reason": p.skipped_reason,
                    "extraction_quality": p.extraction_quality,
                    "chars_kept": p.char_count,
                    "dropped_lines": p.dropped,
                    "warnings": p.warnings,
                }
            )
            if p.skipped_reason:
                warnings.append(f"{doc.document_id} PDF p{p.pdf_page}: SKIPPED - {p.skipped_reason}")
            for w in p.warnings:
                warnings.append(f"{doc.document_id} PDF p{p.pdf_page}: {w}")

    # 6. Embeddings (local model; downloaded once from Hugging Face, then cached)
    log.info("Embedding %d chunks with %s ...", len(all_chunks), settings.embedding_model)
    model = get_embedding_model(settings.embedding_model)
    token_limit = model.max_seq_length
    # independent check: full model input length, including the [CLS]/[SEP] special tokens
    input_lengths = [len(model.tokenizer.encode(c["text"])) for c in all_chunks]
    over_limit = [c["chunk_id"] for c, n in zip(all_chunks, input_lengths) if n > token_limit]
    embeddings = embed_texts([c["text"] for c in all_chunks], settings.embedding_model, show_progress=True)

    # 7. Vector store
    client = get_client(settings.vector_store_dir)
    collection = reset_collection(client, settings.collection_name)
    upsert_chunks(collection, all_chunks, embeddings)

    # Inspection files: chunks/pages are regenerable (git-ignored); the report is small and committed.
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    chunks_path = PROCESSED_DIR / f"{stem}_chunks.jsonl"
    filtered_path = PROCESSED_DIR / f"{stem}_filtered_text.jsonl"
    report_path = settings.metadata_dir / f"{stem}_ingestion_report.json"
    with open(chunks_path, "w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    (PROCESSED_DIR / f"{stem}_page_log.json").write_text(json.dumps(page_log, indent=1, ensure_ascii=False), encoding="utf-8")
    with open(filtered_path, "w", encoding="utf-8") as f:
        for item in filtered:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    by_org = Counter(short_org(c["organization"]) for c in all_chunks)
    by_year = Counter(str(c.get("publication_year") or "unknown") for c in all_chunks)
    report = {
        "manifest": str(manifest_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "manifest_version": manifest.get("manifest_version"),
        "ingested_at": ingested_at,
        "embedding_model": settings.embedding_model,
        "embedding_max_tokens": token_limit,
        "chunks_over_token_limit": len(over_limit),
        "chunk_unit": "tokens (embedding-model tokenizer)",
        "chunk_size": settings.chunk_size,
        "chunk_overlap": settings.chunk_overlap,
        "max_content_tokens": max_tokens,
        "max_model_input_length_observed": max(input_lengths),
        "files_discovered": len(discovered),
        "exact_duplicates_in_folder": len(duplicates),
        "document_count": len(docs),
        "pdf_pages_considered": sum(d["pdf_pages_considered"] for d in per_doc),
        "pdf_pages_indexed": sum(d["pdf_pages_indexed"] for d in per_doc),
        "pdf_pages_skipped": sum(d["pdf_pages_skipped"] for d in per_doc),
        "documents": per_doc,
        "total_chunks": len(all_chunks),
        "chunks_by_organization": dict(sorted(by_org.items())),
        "chunks_by_publication_year": dict(sorted(by_year.items())),
        "hygiene_removed_lines_by_rule": dict(sorted(hygiene_lines.items())),
        "hygiene_log": str(filtered_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "warnings": warnings,
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    # Summary
    sizes = sorted(c["char_count"] for c in all_chunks)
    toks = sorted(c["token_count"] for c in all_chunks)
    pct = lambda q: toks[min(len(toks) - 1, int(q * len(toks)))]  # noqa: E731
    print()
    print("=" * 96)
    print(f"INGESTION SUMMARY: {manifest.get('manifest_version')}")
    print("=" * 96)
    print(f"Files discovered in source folder:   {len(discovered)}  ({len(duplicates)} exact duplicates detected)")
    print(f"Documents selected:                   {len(docs)}")
    print(f"Embedding model:                      {settings.embedding_model} (max {token_limit} tokens)")
    print(f"Chunk size / overlap:                 {settings.chunk_size} / {settings.chunk_overlap} tokens (hard ceiling {max_tokens} content tokens)")
    print()
    print(f"{'document_id':18s}{'org':7s}{'year':>6s}{'pages':>7s}{'indexed':>9s}{'skipped':>9s}{'chunks':>8s}{'highl.':>8s}{'agency':>8s}{'avg tok':>9s}")
    for d in per_doc:
        print(f"{d['document_id']:18s}{short_org(d['organization']):7s}{str(d['publication_year'] or '?'):>6s}{d['pdf_pages_considered']:>7d}"
              f"{d['pdf_pages_indexed']:>9d}{d['pdf_pages_skipped']:>9d}{d['chunks']:>8d}{d['highlights_chunks']:>8d}"
              f"{d['agency_comments_chunks']:>8d}{d['avg_chunk_tokens']:>9d}")
    print(f"{'TOTAL':31s}{report['pdf_pages_considered']:>7d}{report['pdf_pages_indexed']:>9d}"
          f"{report['pdf_pages_skipped']:>9d}{len(all_chunks):>8d}{sum(d['highlights_chunks'] for d in per_doc):>8d}"
          f"{sum(d['agency_comments_chunks'] for d in per_doc):>8d}")
    print()
    print(f"Chunks by organization:               {report['chunks_by_organization']}")
    print(f"Chunks by publication year:           {report['chunks_by_publication_year']}")
    print(f"Chunk length (tokens): min {toks[0]}, 10th pct {pct(0.1)}, median {pct(0.5)}, mean {sum(toks) / len(toks):.0f}, "
          f"90th pct {pct(0.9)}, max {toks[-1]}")
    print(f"Chunks in 180-220 token target band: {sum(180 <= t <= 220 for t in toks)} of {len(toks)}")
    print(f"Chunk length (chars):  min {sizes[0]}, median {sizes[len(sizes) // 2]}, max {sizes[-1]}")
    print(f"Longest model input incl. special tokens: {max(input_lengths)} (limit {token_limit})")
    print(f"Chunks exceeding the model's {token_limit}-token input limit: {len(over_limit)}")
    print(f"Hygiene removals (lines/sentences):   {dict(sorted(hygiene_lines.items()))}")
    print(f"Hygiene log:                          {filtered_path}")
    print(f"Chunks in vector store:               {collection.count()}")
    print(f"Vector store location:                {settings.vector_store_dir}")
    print(f"Ingestion report:                     {report_path}")
    print(f"Chunk dump for inspection:            {chunks_path}")
    print(f"Elapsed:                              {time.time() - start:.0f} s")
    print()
    print(f"WARNINGS ({len(warnings)}):")
    for w in warnings:
        print(f"  - {w}")
    print("=" * 96)


if __name__ == "__main__":
    main()
