"""Answer generation. Both routing tiers are served by Groq (free) — the
`decision.model` string is the only thing that differs between them."""

import time
from dataclasses import dataclass

from groq import Groq

from src.routing.router import RoutingDecision

SYSTEM_PROMPT = (
    "Answer the user's question using only the knowledge graph facts and "
    "document passages provided below. If they don't contain enough "
    "information to answer, say so plainly instead of guessing."
)


@dataclass
class GenerationResult:
    answer: str
    model: str
    tier: str
    latency_seconds: float


def _build_user_content(question: str, context: str) -> str:
    return f"{context}\n\n### Question\n{question}"


def generate_answer(groq_client: Groq, decision: RoutingDecision, question: str, context: str) -> GenerationResult:
    start = time.perf_counter()
    response = groq_client.chat.completions.create(
        model=decision.model,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_content(question, context)},
        ],
    )
    answer = response.choices[0].message.content
    latency = time.perf_counter() - start
    return GenerationResult(answer=answer, model=decision.model, tier=decision.tier, latency_seconds=latency)
