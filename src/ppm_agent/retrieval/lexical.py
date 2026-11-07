"""Lexical retrieval: Okapi BM25 over the indexed chunk texts (no extra dependency).

Standard formulation with the usual defaults k1 = 1.5, b = 0.75 and IDF log(1 + (N - n + 0.5) / (n + 0.5)).
Tokenization: lowercase, runs of letters/digits ("F-35" -> "f", "35"), generic English stopwords
removed, no stemming. Nothing here is domain- or question-specific.
"""

from __future__ import annotations

import math
import re
from collections import Counter

K1 = 1.5
B = 0.75

STOPWORDS = frozenset("""
a about above after again against all am an and any are as at be because been before being below between both but
by can could did do does doing down during each few for from further had has have having he her here hers herself
him himself his how i if in into is it its itself just me more most my myself no nor not of off on once only or other
our ours ourselves out over own same she should so some such than that the their theirs them themselves then there
these they this those through to too under until up very was we were what when where which while who whom why will
with would you your yours yourself yourselves
""".split())

TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN.findall(text.lower()) if t not in STOPWORDS]


class BM25Index:
    """BM25 index over (id, text) pairs, built once in memory."""

    def __init__(self, ids: list[str], texts: list[str], k1: float = K1, b: float = B):
        if len(ids) != len(texts):
            raise ValueError("ids and texts must be the same length")
        self.ids, self.k1, self.b = list(ids), k1, b
        self.term_freqs = [Counter(tokenize(t)) for t in texts]
        self.lengths = [sum(tf.values()) for tf in self.term_freqs]
        self.avg_length = sum(self.lengths) / max(len(self.lengths), 1)
        doc_freq = Counter(term for tf in self.term_freqs for term in tf)
        n = len(ids)
        self.idf = {term: math.log(1 + (n - df + 0.5) / (df + 0.5)) for term, df in doc_freq.items()}

    def scores(self, query: str) -> list[float]:
        """BM25 score of every indexed text for ``query`` (summed over query tokens, repeats included)."""
        terms = [t for t in tokenize(query) if t in self.idf]
        out = []
        for tf, length in zip(self.term_freqs, self.lengths):
            norm = self.k1 * (1 - self.b + self.b * length / self.avg_length)
            out.append(sum(self.idf[t] * tf[t] * (self.k1 + 1) / (tf[t] + norm) for t in terms if t in tf))
        return out

    def search(self, query: str, n: int | None = None) -> list[tuple[str, float]]:
        """(id, score) best first; ties broken by id so the ranking is deterministic. Zero scores are dropped."""
        ranked = sorted((pair for pair in zip(self.ids, self.scores(query)) if pair[1] > 0), key=lambda p: (-p[1], p[0]))
        return ranked if n is None else ranked[:n]
