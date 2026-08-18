"""Lightweight, dependency-free complexity classifier for query routing.

Deliberately a heuristic rather than an LLM call: the entire point of
routing is to decide which model to pay for *before* paying for one.
"""

import re

_COMPLEX_MARKERS = (
    "compare",
    "comparison",
    "why",
    "relationship between",
    "how does",
    "how did",
    "explain",
    "analyze",
    "difference between",
    "versus",
    " vs ",
    "in what way",
    "trace",
    "connect",
    "path between",
)


def complexity_score(question: str) -> float:
    """Return a 0-1 complexity estimate. Higher scores route to the large model."""
    q = question.strip().lower()
    if not q:
        return 0.0

    score = 0.0

    # Longer questions tend to pack in more sub-clauses.
    score += min(len(q.split()) / 30, 0.35)

    # Multiple clauses (commas, "and") suggest multi-hop reasoning.
    score += min(q.count(",") * 0.08, 0.2)
    score += min(q.count(" and ") * 0.1, 0.15)

    # Marker phrases associated with comparative / causal / multi-hop questions.
    if any(marker in q for marker in _COMPLEX_MARKERS):
        score += 0.35

    # More than one capitalized entity-shaped phrase suggests the question
    # spans several graph nodes (checked against the original, not lowered).
    capitalized = set(re.findall(r"\b[A-Z][a-zA-Z]+\b", question))
    if len(capitalized) >= 2:
        score += 0.15

    return min(score, 1.0)
