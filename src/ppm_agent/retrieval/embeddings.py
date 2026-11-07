"""Embeddings with a local sentence-transformers model (no paid API).

The default model, all-MiniLM-L6-v2, produces 384-dimensional vectors and runs
comfortably on a CPU. It is downloaded once from Hugging Face and cached locally.
"""

from __future__ import annotations

from functools import lru_cache


@lru_cache(maxsize=2)
def get_embedding_model(model_name: str):
    """Load the model once per process and reuse it."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def max_input_tokens(model_name: str) -> int:
    """Longest chunk (in content tokens) the model can embed without truncation.

    The model adds two special tokens ([CLS] and [SEP]) to every input, so the
    content limit is max_seq_length - 2 (256 - 2 = 254 for all-MiniLM-L6-v2).
    """
    return get_embedding_model(model_name).max_seq_length - 2


def token_counter(model_name: str):
    """Return a function text -> number of tokens, using the model's own tokenizer."""
    from transformers.utils import logging as hf_logging

    # Counting a long paragraph exceeds the model's 256-token window; that is expected
    # here (we are measuring, not embedding), so silence the length warning.
    hf_logging.set_verbosity_error()
    tokenizer = get_embedding_model(model_name).tokenizer

    @lru_cache(maxsize=200_000)
    def count(text: str) -> int:
        return len(tokenizer.encode(text, add_special_tokens=False))

    return count


def embed_texts(
    texts: list[str],
    model_name: str,
    batch_size: int = 64,
    show_progress: bool = False,
) -> list[list[float]]:
    """Embed a batch of texts. Vectors are L2-normalized so cosine similarity is a dot product."""
    model = get_embedding_model(model_name)
    vectors = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=show_progress,
    )
    return vectors.tolist()


def embed_query(query: str, model_name: str) -> list[float]:
    """Embed a single query string."""
    return embed_texts([query], model_name)[0]
