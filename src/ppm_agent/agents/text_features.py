"""Generic text features used ONLY by the MOCK_AGENT_MODE generator and critic.

These are transparent lexical heuristics, not reasoning. They contain no question- or
document-specific vocabulary: activity terms come from the supplied Activity name and description,
and the cue / intermediate word lists are generic engineering-process language.
"""

from __future__ import annotations

from ppm_agent.models import Activity
from ppm_agent.retrieval.lexical import tokenize

# words that signal a stated dependency or effect (prefix match)
DEPENDENCY_CUES = ("affect", "delay", "hamper", "constrain", "limit", "depend", "because", "result", "caus",
                   "driv", "slow", "prevent", "compress", "imped", "due")
# generic intermediate engineering-process activities (prefix match)
INTERMEDIATE_TERMS = ("integrat", "readiness", "ready", "release", "deliver", "verif", "laborator", "lab",
                      "qualif", "regression", "accredit")
MIN_ACTIVITY_TERM_HITS = 2  # a passage "mentions" an activity when it matches >= 2 of its terms
GENERIC_ACTIVITY_WORDS = frozenset({"activity", "activities", "program", "f", "35"})


def stem(term: str) -> str:
    return term[:5] if len(term) > 5 else term


def activity_terms(activity: Activity) -> list[str]:
    seen = []
    for t in tokenize(f"{activity.name} {activity.description}"):
        s = stem(t)
        if t not in GENERIC_ACTIVITY_WORDS and s not in seen:
            seen.append(s)
    return seen


def passage_features(text: str, source: Activity, target: Activity) -> dict:
    tokens = set(tokenize(text))
    hits = lambda terms: sorted({t for t in terms if any(tok.startswith(t) for tok in tokens)})  # noqa: E731
    src, tgt = hits(activity_terms(source)), hits(activity_terms(target))
    cues = sorted({c for c in DEPENDENCY_CUES if any(tok.startswith(c) for tok in tokens)})
    inter = sorted({c for c in INTERMEDIATE_TERMS if any(tok.startswith(c) for tok in tokens)})
    mentions_source = len(src) >= MIN_ACTIVITY_TERM_HITS
    mentions_target = len(tgt) >= MIN_ACTIVITY_TERM_HITS
    return {
        "source_terms": src, "target_terms": tgt, "cues": cues, "intermediate_terms": inter,
        "mentions_source": mentions_source, "mentions_target": mentions_target,
        "co_mention": mentions_source and mentions_target,
        "stated_dependency": mentions_source and mentions_target and bool(cues),
    }
