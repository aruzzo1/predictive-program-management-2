"""Tests for the vector store and top-k retrieval, using toy 3-d embeddings
so no model download is needed."""

import uuid

import chromadb
import pytest

from ppm_agent.config import get_settings
from ppm_agent.retrieval.retriever import retrieve, retrieve_deduplicated
from ppm_agent.retrieval.vector_store import get_client, get_collection, upsert_chunks


def make_chunk(i, pdf_page, printed_page=None, section_type=None):
    return {
        "chunk_id": f"GAO-11-325-p{pdf_page:03d}-c{i:02d}",
        "text": f"chunk {i}",
        "document_id": "GAO-11-325",
        "filename": "GAO-11-325.pdf",
        "title": "Joint Strike Fighter: Restructuring Places Program on Firmer Footing, but Progress Still Lags",
        "organization": "GAO",
        "publication_date": "2011-04-07",
        "source_type": "GAO report (accessible-text version)",
        "document_hash": "f" * 64,
        "pdf_page": pdf_page,
        "printed_page": printed_page,
        "section_type": section_type,
        "chunk_index": i,
    }


CHUNKS = [make_chunk(i, pdf_page=i + 1, section_type="highlights" if i == 0 else None) for i in range(8)]
# chunk 0 points exactly along the query; the others are progressively further away
VECTORS = [[1.0, 0.0, 0.0]] + [[1.0 - i * 0.12, i * 0.12, 0.0] for i in range(1, 8)]


def build_collection():
    collection = get_collection(chromadb.EphemeralClient(), name=f"test_{uuid.uuid4().hex}")
    upsert_chunks(collection, CHUNKS, VECTORS)
    return collection


def query_vector(_query):
    return [1.0, 0.0, 0.0]


def test_retrieve_returns_top_5_ranked_results():
    results = retrieve("anything", top_k=5, collection=build_collection(), embed_fn=query_vector)

    assert len(results) == 5
    assert [r["rank"] for r in results] == [1, 2, 3, 4, 5]
    assert results[0]["chunk_id"] == "GAO-11-325-p001-c00"
    distances = [r["distance"] for r in results]
    assert distances == sorted(distances)


def test_top_k_is_configurable():
    results = retrieve("anything", top_k=3, collection=build_collection(), embed_fn=query_vector)
    assert len(results) == 3


def test_retrieved_results_preserve_metadata():
    result = retrieve("anything", top_k=1, collection=build_collection(), embed_fn=query_vector)[0]

    assert result["document_id"] == "GAO-11-325"
    assert result["organization"] == "GAO"
    assert result["pdf_page"] == 1
    assert result["printed_page"] is None  # unknown printed page stays null, not invented
    assert result["section_type"] == "highlights"
    assert result["metadata"]["document_hash"] == "f" * 64
    assert result["metadata"]["publication_date"] == "2011-04-07"


def test_overlapping_adjacent_chunk_is_suppressed():
    shared = "development of mission systems software continued to experience delays that affected flight test progress"
    chunks = [make_chunk(i, pdf_page=10 + i) for i in range(8)]
    chunks[0].update(text=f"Opening point. {shared}.", pdf_page=29)
    chunks[1].update(chunk_id="GAO-11-325-p029-c01", text=f"{shared}. A different follow-on point.", pdf_page=29)
    collection = get_collection(chromadb.EphemeralClient(), name=f"test_{uuid.uuid4().hex}")
    upsert_chunks(collection, chunks, VECTORS)  # chunk 1 is the second-closest to the query

    out = retrieve_deduplicated("anything", top_k=5, collection=collection, embed_fn=query_vector,
                                candidate_k=6, min_shared_words=12)

    ids = [r["chunk_id"] for r in out["results"]]
    assert "GAO-11-325-p029-c01" not in ids  # lower-scoring duplicate removed
    assert ids[0] == chunks[0]["chunk_id"]  # higher-scoring one kept
    assert len(ids) == 5  # list refilled from further down the ranking
    assert out["suppressed"][0]["duplicate_of"] == chunks[0]["chunk_id"]


def test_vector_store_persists_across_clients(tmp_path):
    store = tmp_path / "chroma"
    upsert_chunks(get_collection(get_client(store), "persist_test"), CHUNKS, VECTORS)

    reopened = get_collection(get_client(store), "persist_test")  # a fresh client on the same folder

    assert reopened.count() == len(CHUNKS)
    results = retrieve("anything", top_k=5, collection=reopened, embed_fn=query_vector)
    assert results[0]["chunk_id"] == "GAO-11-325-p001-c00"


def test_real_store_result_exposes_pdf_page():
    """Regression: a result from the real ingested store carries pdf_page, not the old 'page' key.

    Read-only; uses the real embedding model. Skipped if the store has not been built.
    """
    settings = get_settings()
    if not (settings.vector_store_dir / "chroma.sqlite3").is_file():
        pytest.skip("vector store not built; run scripts/ingest_corpus.py")

    result = retrieve("F-35 software maturity and flight test", top_k=1)[0]

    assert isinstance(result["pdf_page"], int)
    assert "page" not in result
    assert "page" not in result["metadata"]
    assert "printed_page" in result
