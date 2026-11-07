"""Retrieval agent: build a grounded prompt from retrieved chunks and, if an
OpenAI key is configured, generate an answer that uses only that evidence.

Without a key, the agent runs in retrieval-only mode: it still builds the
grounded prompt (saved in the trace) but does not call an LLM.
"""

from __future__ import annotations

DEFAULT_DEPENDENCY = "Mission-System Software Maturity → Flight-Test Execution"

VERDICT_LABELS = ["SUPPORTED", "PARTIALLY SUPPORTED", "NOT SUPPORTED", "INSUFFICIENT EVIDENCE"]

SYSTEM_PROMPT = """You are a careful program-analysis assistant. You answer questions about the
F-35 / Joint Strike Fighter program using ONLY the evidence passages provided by the user.

Rules:
1. Answer only from the retrieved evidence. Do not use outside knowledge.
2. Cite every factual statement as [filename, p. N] using the filename and PDF page shown in the
   passage's Citation line.
3. Clearly label each point as DIRECT EVIDENCE (the passage states it) or INFERENCE
   (your reasoning connecting passages). Never present an inference as a stated fact.
4. Do not use causal language (caused, led to, resulted in, due to) unless a passage states
   the causal link itself; otherwise describe the relationship as an association or inference.
5. If the evidence is insufficient to answer, say so explicitly. Do not invent missing facts,
   dates, numbers, or sources."""


def format_evidence(chunks: list[dict]) -> str:
    """Render retrieved chunks as numbered evidence blocks with their citations.

    The citation page is the PDF page (pdf_page); the printed page is shown
    alongside it when it is known.
    """
    blocks = []
    for chunk in chunks:
        printed = f" (printed page {chunk['printed_page']})" if chunk.get("printed_page") else ""
        blocks.append(
            f"[Evidence {chunk['rank']}] Citation: [{chunk['filename']}, p. {chunk['pdf_page']}]{printed}\n"
            f"{chunk['text'].strip()}"
        )
    return "\n\n---\n\n".join(blocks)


def build_grounded_prompt(question: str, chunks: list[dict], dependency: str = DEFAULT_DEPENDENCY) -> str:
    """Build the user message containing the question, evidence, and output format."""
    labels = " | ".join(VERDICT_LABELS)
    return f"""QUESTION:
{question}

RETRIEVED EVIDENCE ({len(chunks)} passages):

{format_evidence(chunks)}

INSTRUCTIONS:
Using only the evidence above, write:

1. ANSWER — a concise answer to the question. Mark each point DIRECT EVIDENCE or INFERENCE,
   and cite it as [filename, p. N].
2. EVIDENCE GAPS — what the retrieved passages do not establish.
3. DEPENDENCY ASSESSMENT — evaluate the candidate dependency:
   "{dependency}"
   Give exactly one line in the form:
   DEPENDENCY VERDICT: <one of {labels}>
   then explain why, citing the passages. Use INSUFFICIENT EVIDENCE if the passages do not
   discuss both sides of the relationship."""


def generate_answer(prompt: str, api_key: str, model: str) -> str:
    """Call the OpenAI chat API with temperature 0 and return the answer text."""
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


def answer(
    question: str,
    chunks: list[dict],
    api_key: str | None = None,
    model: str = "gpt-4o-mini",
    dependency: str = DEFAULT_DEPENDENCY,
) -> dict:
    """Return {"mode", "model", "prompt", "answer", "error"}.

    mode is "grounded-generation" if an answer was produced, otherwise "retrieval-only".
    """
    prompt = build_grounded_prompt(question, chunks, dependency)
    result = {"mode": "retrieval-only", "model": None, "prompt": prompt, "answer": None, "error": None}
    if not api_key:
        return result
    try:
        result["answer"] = generate_answer(prompt, api_key, model)
        result["mode"] = "grounded-generation"
        result["model"] = model
    except Exception as exc:  # report the failure instead of hiding it
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result
