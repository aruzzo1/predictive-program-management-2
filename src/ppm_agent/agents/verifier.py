"""A simple, transparent grounding verifier.

It does not judge truth. It applies three rule-based checks meant to catch
the most common forms of false grounding:

1. Evidence coverage — does at least one retrieved passage mention BOTH sides
   of the claimed relationship (e.g., software maturity AND flight testing)?
   A passage about only one side cannot support a dependency.
2. Source metadata — does the answer cite [filename, p. N], and does every
   citation point to a passage that was actually retrieved?
3. Causal language — does the answer use causal wording (caused, led to, ...)
   in a sentence with no citation, or causal wording that never appears in the
   evidence? Either suggests causality was added by the model.

Limitation: keyword co-occurrence is not proof of a relationship. These checks
flag likely problems; a human still reads the evidence.
"""

from __future__ import annotations

import re

# Terms for each side of the default dependency
# "Mission-System Software Maturity → Flight-Test Execution".
SOFTWARE_TERMS = ["software", "mission system", "block 2b", "block 3", "block 3f", "block 3i"]
FLIGHT_TEST_TERMS = [
    "flight test",
    "test flight",
    "test point",
    "flight sciences",
    "sortie",
    "test aircraft",
    "developmental test",
]

CAUSAL_PHRASES = [
    "caused",
    "causes",
    "causing",
    "led to",
    "leads to",
    "resulted in",
    "results in",
    "due to",
    "because of",
    "as a result of",
    "attributable to",
    "drove",
    "driven by",
]

CITATION_PATTERN = re.compile(r"\[([^\[\]]+?),\s*p\.?\s*(\d+)\]")


def normalize(text: str) -> str:
    """Lowercase and treat hyphens/newlines as spaces so 'flight-\\ntest' matches 'flight test'."""
    text = text.lower().replace("-\n", "").replace("-", " ")
    return re.sub(r"\s+", " ", text)


def matching_terms(text: str, terms: list[str]) -> list[str]:
    norm = normalize(text)
    return [t for t in terms if t in norm]


def check_evidence_coverage(
    chunks: list[dict],
    cause_terms: list[str] = SOFTWARE_TERMS,
    effect_terms: list[str] = FLIGHT_TEST_TERMS,
) -> dict:
    """Check 1: which retrieved passages mention both sides of the relationship."""
    per_passage = []
    for chunk in chunks:
        cause = matching_terms(chunk["text"], cause_terms)
        effect = matching_terms(chunk["text"], effect_terms)
        per_passage.append(
            {
                "rank": chunk["rank"],
                "filename": chunk["filename"],
                "pdf_page": chunk["pdf_page"],
                "printed_page": chunk.get("printed_page"),
                "cause_terms": cause,
                "effect_terms": effect,
                "both_sides": bool(cause and effect),
            }
        )
    both = [p["rank"] for p in per_passage if p["both_sides"]]
    return {"passed": bool(both), "ranks_with_both_sides": both, "per_passage": per_passage}


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]


def check_citations(answer: str, chunks: list[dict]) -> dict:
    """Check 2: citations exist and match retrieved (filename, pdf_page) pairs."""
    retrieved = {(c["filename"], int(c["pdf_page"])) for c in chunks}
    cited = [(name.strip(), int(page)) for name, page in CITATION_PATTERN.findall(answer)]
    valid = [c for c in cited if c in retrieved]
    invalid = [c for c in cited if c not in retrieved]
    return {
        "passed": bool(cited) and not invalid,
        "citations_found": len(cited),
        "valid_citations": sorted(set(valid)),
        "citations_not_in_retrieved_evidence": sorted(set(invalid)),
    }


def check_causal_language(answer: str, chunks: list[dict]) -> dict:
    """Check 3: causal wording that is uncited or absent from the evidence."""
    evidence = normalize(" ".join(c["text"] for c in chunks))
    uncited = []
    used = set()
    for sentence in split_sentences(answer):
        found = [p for p in CAUSAL_PHRASES if p in normalize(sentence)]
        if not found:
            continue
        used.update(found)
        if not CITATION_PATTERN.search(sentence):
            uncited.append(sentence)
    not_in_evidence = sorted(p for p in used if p not in evidence)
    return {
        "passed": not uncited and not not_in_evidence,
        "causal_phrases_used": sorted(used),
        "uncited_causal_sentences": uncited,
        "causal_phrases_not_in_evidence": not_in_evidence,
    }


def find_verdict(answer: str) -> str | None:
    match = re.search(
        r"DEPENDENCY VERDICT:\s*\**\s*(PARTIALLY SUPPORTED|NOT SUPPORTED|INSUFFICIENT EVIDENCE|SUPPORTED)",
        answer,
        flags=re.IGNORECASE,
    )
    return match.group(1).upper() if match else None


def verify_grounding(answer: str | None, chunks: list[dict]) -> dict:
    """Run all checks. With no answer (retrieval-only mode) only the evidence check runs."""
    report = {"evidence_coverage": check_evidence_coverage(chunks)}
    if answer is None:
        report["citations"] = report["causal_language"] = None
        report["verdict"] = None
        report["overall"] = "PASS" if report["evidence_coverage"]["passed"] else "WARN"
        report["notes"] = "Retrieval-only mode: answer checks not run."
        return report

    report["citations"] = check_citations(answer, chunks)
    report["causal_language"] = check_causal_language(answer, chunks)
    report["verdict"] = find_verdict(answer)

    problems = []
    if not report["evidence_coverage"]["passed"]:
        problems.append("no retrieved passage discusses both sides of the relationship")
    if not report["citations"]["passed"]:
        problems.append("missing or unmatched citations")
    if not report["causal_language"]["passed"]:
        problems.append("possible unsupported causal language")
    if report["verdict"] is None:
        problems.append("no dependency verdict found")
    if report["verdict"] in ("SUPPORTED", "PARTIALLY SUPPORTED") and not report["evidence_coverage"]["passed"]:
        problems.append("verdict claims support but evidence coverage check failed")

    report["overall"] = "PASS" if not problems else "WARN"
    report["notes"] = "; ".join(problems) if problems else "All checks passed."
    return report
