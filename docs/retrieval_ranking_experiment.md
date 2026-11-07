# Retrieval Ranking Experiment: RAG_RANKING_V2_1

> **Historical document from the RAG development phase.** Its findings remain valid for that phase. The final, frozen
> implementation is described in [`technical_freeze.md`](technical_freeze.md).

## Problem

The RAG_EXPANDED_V2 corpus (10 documents, 848 chunks) already contains evidence that plain
semantic top-k retrieval does not reliably surface:

- **Q02 (requirements / KPPs):** key-performance-parameter evidence is indexed (GAO-05-271
  p.10-11, GAO-07-360 p.17-18, GAO-08-388 p.15) but does not reach the top five.
- **Q08 (concurrency):** at least 46 indexed chunks mention concurrency, including explicit
  material in GAO-06-356 (e.g. p.6, "a highly concurrent approach that makes significant
  investments in manufacturing capabilities and production aircraft before flight testing
  demonstrates the JSF's performance") and GAO-05-271. None reaches the top five.
- **Q12 (downstream cost / retrofit):** qualitative retrofit and concurrency-cost statements exist
  in several documents (e.g. GAO-08-388 p.23, GAO-05-271 p.15) but do not rank well.

This experiment tests **retrieval ranking only**. It is not corpus expansion: no document is added
or removed, and the embedding model, chunk size (220 tokens), overlap (35), top_k (5) and the
duplicate-suppression rule are unchanged. Every strategy ranks the same 848 indexed chunk texts.

Two questions have special status:

- **Q07 (weight growth) is not a tuning target.** Where the explicit GAO-08-388 p.34 passage ranks
  is reported, along with whether intermediate fragments of the distributed dependency appear.
  Nothing is optimized for it.
- **Q13 (Block 4 / TR-3) is a temporal-control case.** Its valid evidence comes from DOT&E FY2024.
  It is used to demonstrate that a historical analysis date excludes later evidence.

## Baseline

RAG_EXPANDED_V2 is frozen as the comparison baseline. File and store hashes are in
`data/metadata/rag_expanded_v2_freeze.json`, and artifact copies are in
`data/processed/rag_expanded_v2/`. Its outputs (`outputs/evaluation/rag_expanded_v2.*`,
`rag_v1_v2_comparison.md`) are not modified.

## Strategies (fixed before any evaluation run)

| Name | Ranking |
|---|---|
| `SEMANTIC_V2` | Existing dense retrieval, unchanged (Chroma cosine search, candidate_k 15, near-duplicate suppression). Must reproduce RAG_EXPANDED_V2 exactly. |
| `BM25_V2_1` | Okapi BM25 over the same chunk texts. |
| `HYBRID_V2_1` | Reciprocal Rank Fusion of the dense and BM25 rankings. |
| `HYBRID_RERANKED_V2_1` | The hybrid candidate pool re-scored by a local cross-encoder. |

All strategies apply the same near-duplicate suppression (same document, page within 1, at least
12 shared consecutive words) to their final ranking before taking the top 5.

**BM25.** The parameters are the standard defaults k1 = 1.5 and b = 0.75, with the usual Okapi
IDF, log(1 + (N - n + 0.5) / (n + 0.5)). Tokenization lowercases the text and splits on runs of
letters and digits, so "F-35" becomes "f", "35". Tokens of a generic English stopword list (articles,
prepositions, pronouns, auxiliaries) are dropped. There is no stemming and no domain or
question-specific vocabulary. The query is tokenized the same way. The implementation is in-house
(`ppm_agent.retrieval.lexical`), about 60 lines, so no dependency is added.

**Hybrid (RRF).** score(d) = 1/(60 + rank_dense(d)) + 1/(60 + rank_bm25(d)). The constant k = 60 is
the standard value from Cormack, Clarke & Büttcher (2009) and is not tuned. Candidate pools are the
top 30 dense and top 30 BM25 chunks (2 × candidate_k). A chunk absent from one pool contributes only
its other term. Ties are broken by chunk_id for determinism. The dense pool is an exact
dot-product ranking over the stored normalized embeddings.

**Reranked hybrid.** The union of the two 30-chunk pools is scored with
`cross-encoder/ms-marco-MiniLM-L-6-v2`, a 22M-parameter MS MARCO passage reranker run locally
through the already installed `sentence-transformers`. Its maximum input is 512 tokens, and the
query plus a ≤254-token chunk fits. It is not trained or tuned on the evaluation questions.

## Temporal controls

Each chunk's temporal status is derived from its stored metadata. No date is invented, and an
approximate date is never promoted to a verified one.

| temporal_status | Condition |
|---|---|
| `VERIFIED_PUBLICATION_DATE` | publication_date is set |
| `APPROXIMATE_AVAILABILITY` | no publication_date, but content_not_before (YYYY-MM of a dated event in the text) is set |
| `UNDATED_REQUIRES_REVIEW` | neither |

With an `analysis_date`, each chunk is classified as follows:

| temporal_status | Condition | Eligibility |
|---|---|---|
| Verified | publication_date ≤ analysis_date | ELIGIBLE |
| Verified | publication_date > analysis_date | INELIGIBLE |
| Approximate | analysis_date is before the start of the content_not_before month (the document describes later events, so it cannot have existed) | INELIGIBLE |
| Approximate | otherwise | REQUIRES_REVIEW (an explicit `approximate_policy="assume_available"` override makes it ELIGIBLE) |
| Undated | — | REQUIRES_REVIEW |

Only ELIGIBLE chunks are ranked. REQUIRES_REVIEW chunks are reported separately and never silently
included. Without an analysis_date, retrieval is unchanged.

## Evaluation

The same 13 questions (`data/metadata/rag_evaluation_questions.json`, unedited) are run through
each strategy. Scores from different strategies are not comparable, so no strategy is judged
better on its scores. The comparison looks at:
- whether known relevant passages surface;
- source diversity;
- wrong-topic results;
- hub-chunk frequency;
- duplicate behaviour;
- the known retrieval-miss questions.

Keyword checks used in the report, such as "does a top-5 passage mention key performance
parameters / concurrency", are diagnostics for reading the results. They are not part of any
retrieval strategy. Human review remains the relevance judgment.

Results: `outputs/evaluation/rag_ranking_v2_1_comparison.md`. Runner: `python scripts/run_retrieval_benchmark.py`.

## Findings (2026-10-25, preliminary pending human review)

- `SEMANTIC_V2` reproduces RAG_EXPANDED_V2 exactly, for all 13 questions.
- Partly corrected retrieval misses:
  - Q02: KPP evidence (BM25, reranked);
  - Q08: explicit concurrency from GAO-07-360 (BM25, hybrid, reranked);
  - Q12: qualitative retrofit evidence (all three alternatives).
- Q08 for GAO-06-356 is not corrected under any strategy. Its passages use only *concurrent* and
  *concurrently*, and the pre-registered tokenizer has no stemming, so they share no term with the
  query's *concurrency*. Stemming (e.g. Porter or Snowball) is the obvious next variant. Adopting it
  now, after seeing these results, would be tuning on the evaluation set, so it should be specified
  first and then evaluated on questions not used to design it.
- BM25 alone introduces off-topic term matches (generic "requirements", "test", "software") and
  more near-duplicates. Hybrid and reranked are in between.
- DOT&E share of results: semantic 54%, BM25 34%, hybrid 45%, reranked 42%. The FY2024 p.2 hub
  appears in 7 / 2 / 5 / 3 questions.
- Temporal control works under every strategy. At an analysis date of 2011-12-31, the DOT&E FY2024
  chunks are INELIGIBLE (60), the DOT&E FY2010 chunks are REQUIRES_REVIEW (34, not included), and
  every returned chunk has a verified publication date of 2011 or earlier.
